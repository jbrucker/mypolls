from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib.auth.models import User
from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    """Show a list of published polls."""
    template_name = 'polls/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        """
        Return all available poll questions.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


def detail(request, question_id):
    """Display details for a single question.
     
      :param question_id: id of the question to display.
    """
    try:
        q: Question = Question.objects.get(id=question_id)
        # don't show future questions
        if not q.is_published(): raise Question.DoesNotExist
    except Question.DoesNotExist:
        return HttpResponseNotFound(f"Question id {question_id} not found." )

    # include the user's prior vote in the context
    vote = Vote.get_vote(question=q, user=request.user)
    choice = vote.choice.id if vote and vote.choice else 0
    context = {"question": q, "selected_choice": choice}
    return render(request, 'polls/detail.html', context)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


@login_required
def vote(request, question_id):
    """Handle a vote submissed by a user for a poll question."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "You didn't select a valid choice.")
        return render(request, 'polls/detail.html', {'question': question})
    # is voting allowed?
    if not question.can_vote():
        messages.error(request, 
                 f'Voting not currently accepted for "{question.question_text}".')
        return redirect('polls:index')

    this_user = request.user
    # update his vote or create a new vote?
    vote = Vote.get_vote(question=question, user=this_user)
    if vote:
        vote.choice = selected_choice
    else:
        # create a new vote
        vote = Vote(user=this_user, choice=selected_choice)
    vote.save()
    messages.info(request, f"Your vote for {selected_choice.choice_text} has been recorded.")
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))