# import json
# import re
#
# import pytest
#
# from cromshell.cost import command as cost_command

# class TestCost:
#     """Test the execution of cost command functions"""
#
#     # def test_query_bigquery(self):
#
#     @pytest.mark.parametrize(
#         "detailed, bq_cost_table",
#         [
#             [
#                 True,
#                 "cost:table:1",
#             ],
#             [
#                 False,
#                 "cost:table1",
#             ],
#         ],
#     )
#     def test_create_bq_query(self, detailed, bq_cost_table):
#         query = cost_command.create_bq_query(
#             detailed=detailed, bq_cost_table=bq_cost_table
#         )


# def test_create_bq_query_job_config(self):
# def test_check_bq_query_results(self):
# def test_check_bq_query_for_errors(self):
# def test_minimum_time_passed_since_workflow_completion(self):
# def test_get_submission_start_end_time(self):
# def test_checks_before_query(self):
# def test_round_cost_values(self):
# def test_color_cost_outliers(self):
# def test_print_query_results(self):
