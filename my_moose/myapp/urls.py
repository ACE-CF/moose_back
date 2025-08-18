# myapp/urls.py
from django.urls import path
from .views import download_moose1_tree,download_moose2_tree,analyze, load_file_tree,rank_view2,get_last_hypothesis ,rank_view,get_hypothesis_details,load_tree,get_feedback_moose1,get_feedback_moose2,get_tree2_view

urlpatterns = [
    path('analyze/', analyze, name='analyze'),
    path('load_tree/', load_tree, name='load_tree'),
    path('rank/', rank_view, name='rank'),
    path('rank2/', rank_view2, name='rank'),
    path('get_feedback_moose1/', get_feedback_moose1, name='get_feedback_moose1'),
    path('get_feedback_moose2/', get_feedback_moose2, name='get_feedback_moose2'),
    path('hypothesis_details/', get_hypothesis_details, name='hypothesis_details'),
    path('get_tree2_view/', get_tree2_view, name='get_tree2_view'),
    path('analyze/last/', get_last_hypothesis, name='get_last_hypothesis'),
    path('loadfile/', load_file_tree, name='load_file_tree'),
    path('download/moose1_tree/', download_moose1_tree, name='download_moose1_tree'),
    path('download/moose2_tree/', download_moose2_tree, name='download_moose2_tree'),
]