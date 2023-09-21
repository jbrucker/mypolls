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
        super().setUp()
        self.username = "user1"
        self.password = "FatChance"
        self.user1 = User.objects.create_user(
                    self.username, password=self.password)

    def test_login_required_to_vote(self):
        """An unauthenicated request cannot submit a vote."""
        # unauthenticated user is directed to login
        question1 = create_question("Question 1", days=-10)
        choices = create_choices(question1, 3)
        selected_choice = choices[0]
        url = reverse('polls:vote', args=(question1.id,))
        post_data = { 'choice': selected_choice.id}
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
        url = reverse('polls:vote', args=(question1.id,))
        post_data = { 'choice': selected_choice.id}
        # "login" the user to the session
        self.assertTrue(
            self.client.login(username=self.username, password=self.password))
        # should not be any votes yet
        self.assertEqual(selected_choice.votes, 0)
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
        url = reverse('polls:vote', args=(question1.id,))
        post_data = { 'choice': selected_choice.id}
        # "login" the user to the session
        self.assertTrue(
            self.client.login(username=self.username, password=self.password))
        # should not be any votes yet
        self.assertEqual(0, selected_choice.votes)
        # submit a vote!
        response = self.client.post(url, post_data)
        # should redirect polls index with an error message
        self.assertRedirects(response, reverse('polls:index'))
        # and no vote was recorded
        self.assertEqual(0, selected_choice.votes)

    def test_cannot_vote_for_choice_not_this_question(self):
        """Cannot vote for a choice that is not part of this question."""
        question1 = create_question("Question1", days=-1)
        choices1 = create_choices(question1, 3)
        question2 = create_question("Question2", days=-2)
        choices2 = create_choices(question2, 4)
        # select a choice that doesn't belong to question1
        selected_choice = choices2[0]
        url = reverse('polls:vote', args=(question1.id,))
        post_data = { 'choice': selected_choice.id}
        # "login" the user to the session
        self.assertTrue(
            self.client.login(username=self.username, password=self.password))
        # should not be any votes yet
        self.assertEqual(0, selected_choice.votes)
        # submit a vote!
        response = self.client.post(url, post_data)
        # should redisplay polls detail page with an error message
        redirect_url = reverse('polls:detail', args=(question1.id,))
        self.assertRedirects(response, redirect_url)
        # and no vote was recorded
        self.assertEqual(0, selected_choice.votes)

