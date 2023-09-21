"""Tests of voting."""
import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import *

def create_question(question_text, days, ends=None):
    """
    Create a question with the given `question_text` and published the
    given number of `days` from today.
    :param days: publication date offset from today. days < 0 for a question 
                 published in the past, days > 0 for a question not yet published
    :param ends: voting end date offset from today. ends > 0 for an end date in 
                 the future, ends < 0 for poll already closed. 
                 If omitted or None, the question has no ending date.

    Examples:
    # Question published already, no end date
    q1 = create_question("Vote for me", days=-10)
    # Question published 3 days in the future, no end date
    q2 = create_question("Is this the future?", days=3)
    # published 30 days ago, ended 10 days ago
    q3 = create_question("Closed Question", days=-30, end=-10)
    """
    pub_time = timezone.now() + datetime.timedelta(days=days)
    if ends:
        end_time = timezone.now() + datetime.timedelta(days=days)
        end_time.hour = 23
        end_time.minute = 59
        end_time.second = 59
    else:
        end_time = None
    return Question.objects.create(question_text=question_text, 
                                   pub_date=pub_time, end_date=end_time)

def create_choices(question: Question, num_choices=2):
    """Create and save some choices for a question.

    Returns the choices as a list.
    """
    counter = question.choice_set.all().count()
    choices = []
    for n in range(1, num_choices+1):
        counter += 1;
        choice = Choice.objects.create(choice_text=f"Choice {counter}",
                              question=question )
        choices.append(choice)
    return choices


class VotingTest(TestCase):

    def setUp(self):
        """Create a test fixture before each test."""
        super().setUp()
        # Create two users. The tests need to know the username and password,
        # so the user can "login" to the test client session.
        self.username1 = "user1"
        self.password1 = "FatChance"
        self.user1 = User.objects.create_user(
                    self.username1, password=self.password1)
        # another user, so you can create votes not owned by user1
        self.username2 = "user2"
        self.password2 = "FatChance"
        self.user2 = User.objects.create_user(
                    self.username2, password=self.password2)

    def login(self, user: User):
        """Utility function to 'login' a user to the Client session.
           This is needed in many tests.
           :param user: must be self.user1 or self.user2 
        """
        # "login" the user to the client session
        if user == self.user1:
            self.assertTrue( self.client.login(
                        username=self.username1, password=self.password1) )
        elif user == self.user2:
            self.assertTrue( self.client.login(
                        username=self.username2, password=self.password2) )
        else:
            self.fail(f"Unrecognized user parameter {user.username}")

    def test_login_required_to_vote(self):
        """An unauthenicated request cannot submit a vote."""
        # and he is  is redirected to login
        question1 = create_question("Question 1", days=-10)
        choices = create_choices(question1, 3)
        selected_choice = choices[0]
        url = reverse('polls:vote', args=(question1.id,))
        # submit a POST request containing the choice to vote for
        post_data = { 'choice': selected_choice.id }
        response = self.client.post(url, post_data)

        # should redirect to 'login' with appended "?next=/some/url"
        expect_url = reverse('login') + f"?next={url}"
        self.assertRedirects(response, expect_url)
        # and no vote was recorded
        self.assertEqual(0, selected_choice.votes)

    def test_authorized_user_can_vote(self):
        """An authorized user can vote for an active poll."""
        question1 = create_question("Question 1", days=-10)
        choices = create_choices(question1, 3)
        selected_choice = choices[0]
        # this choice should not have any votes yet
        self.assertEqual(selected_choice.votes, 0)
        # must login to vote
        self.login(self.user1)
        # POST a vote to the "vote" url for this question
        url = reverse('polls:vote', args=(question1.id,))
        post_data = { 'choice': selected_choice.id}
        # submit a vote!
        response = self.client.post(url, post_data)
        # should redirect to the results page
        results_url = reverse('polls:results', args=(question1.id,))
        self.assertRedirects(response, results_url)
        # and a vote was recorded for this choice
        self.assertEqual(selected_choice.votes, 1)

    def test_cannot_vote_for_future_poll(self):
        """Cannot vote for a poll that is not published yet."""
        question1 = create_question("Future Question", days=10) # 10 days in future
        choices = create_choices(question1, 3)
        selected_choice = choices[1]
        # should not have any votes yet
        self.assertEqual(0, selected_choice.votes)
        # must login to vote. Login as user1
        self.login(self.user1)
        # POST a vote to the "vote" url for this question
        url = reverse('polls:vote', args=(question1.id,))
        post_data = { 'choice': selected_choice.id}
        response = self.client.post(url, post_data)
        # should redirect to polls index with an error message
        self.assertRedirects(response, reverse('polls:index'))
        # and no vote was recorded
        self.assertEqual(0, selected_choice.votes)

    def test_cannot_vote_for_choice_not_this_question(self):
        """Cannot vote for a choice that is not part of this question."""
        question1 = create_question("Question1", days=-1)
        choices1 = create_choices(question1, 3)
        question2 = create_question("Question2", days=-2)
        choices2 = create_choices(question2, 4)
        # select a choice that doesn't belong to question1 (belongs to question2)
        selected_choice = choices2[0]
        # should not have any votes yet
        self.assertEqual(0, selected_choice.votes)
        # must login in order to vote
        self.login(self.user1)
        # POST a vote to the 'vote' url for question1
        url = reverse('polls:vote', args=(question1.id,))
        post_data = { 'choice': selected_choice.id}
        # submit a vote!
        response = self.client.post(url, post_data)
        # should redisplay polls detail page with an error message
        redirect_url = reverse('polls:detail', args=(question1.id,))
        self.assertRedirects(response, redirect_url)
        # and no vote was recorded
        self.assertEqual(0, selected_choice.votes)

        # TODO write 4 tests for the delete_vote view.
        # In your tests, remember to "login" a user to the test client,
        # as done in the above tests.

        # Example test:

        def test_delete_vote_invalid_vote_id(self):
            """Calling delete_vote with vote id that does not exist should raise 404 error."""
            pass

