"""Models for the ku-polls application."""
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=100)
    # automatically set pub_date to the current date & time
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('closing date', null=True, blank=True)

    def is_published(self):
        """Test if a poll question has been published."""
        return self.pub_date <= timezone.localtime(timezone.now())

    def can_vote(self):
        """Test if voting is currently allowed for this poll."""
        if not self.is_published():
            return False
        localtime = timezone.localtime(timezone.now())
        # if poll has end_date then check it, else voting is always allowed
        return localtime < self.end_date if self.end_date else True

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    # setting for the admin interface
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=80)

    def __str__(self):
        return self.choice_text

    @property
    def votes(self):
        """The number of votes for this choice."""
        return self.vote_set.count()


class Vote(models.Model):
    """Records a Vote for a Choice by a User."""
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def get_vote(cls, question: Question, user: User):
        """Return the vote by a user for a specific poll question.
        
        :param question: a Question to get user's vote for
        :param user: a User whose vote to return
        :returns: the user's vote for the requested question, or None if no vote
        """
        if not user or not user.is_authenticated:
            return None
        try:
            return Vote.objects.get(user=user, choice__question=question)
        except Vote.DoesNotExist:
            # no vote yet
            return None

    def __str__(self):
        return f'Vote by {self.user.username} for {self.choice.choice_text}'