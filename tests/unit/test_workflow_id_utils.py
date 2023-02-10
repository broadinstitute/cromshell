import pytest

from cromshell.utilities import workflow_id_utils


class TestWorkflowIdUtils:
    """Test the functions for workflow_id_utils"""

    @pytest.mark.parametrize(
        "cromshell_input, resolved_workflow_id",
        [
            ["1", "a63aa10c-a43e-4ca7-9be9-c2d2aa08b96d"],  # test digit
            ["trouble", "d689adec-c600-4e4b-be37-4e30e65848c7"],  # test alias
            [
                "fb039687-c2ec-4252-9dea-1e761ced3200",
                "fb039687-c2ec-4252-9dea-1e761ced3200",
            ],  # test workflow id
        ],
    )
    def test_resolve_workflow_id(
        self,
        cromshell_input: str,
        resolved_workflow_id: str,
        tmp_submission_file: str,
    ):
        assert (
            workflow_id_utils.resolve_workflow_id(
                cromshell_input=cromshell_input,
                submission_file_path=tmp_submission_file,
            )
            == resolved_workflow_id
        )

    @pytest.mark.parametrize(
        "relative_id, workflow_id, should_fail",
        [
            [1, "a63aa10c-a43e-4ca7-9be9-c2d2aa08b96d", False],
            [-1, "d7cad898-f13a-4547-b301-f0c9dbb8865d", False],
            [0, "should fail", True],  # zero is not a valid number
            [100, "should fail", True],  # relative_id > rows in submission file
        ],
    )
    def test_obtain_workflow_id_using_digit(
        self,
        relative_id: int,
        workflow_id: str,
        tmp_submission_file: str,
        should_fail,
    ):
        if should_fail:
            with pytest.raises(ValueError):
                workflow_id_utils.obtain_workflow_id_using_digit(
                    relative_id=relative_id, submission_file_path=tmp_submission_file
                )

        else:
            assert (
                workflow_id_utils.obtain_workflow_id_using_digit(
                    relative_id=relative_id, submission_file_path=tmp_submission_file
                )
                == workflow_id
            )

    @pytest.mark.parametrize(
        "alias_name, workflow_id, should_fail",
        [
            ["trouble", "d689adec-c600-4e4b-be37-4e30e65848c7", False],
            ["notexistalias", "should fail", True],
        ],
    )
    def test_obtain_workflow_id_using_alias(
        self,
        alias_name: str,
        workflow_id: str,
        tmp_submission_file: str,
        should_fail: bool,
    ):
        if should_fail:
            with pytest.raises(ValueError):
                workflow_id_utils.obtain_workflow_id_using_alias(
                    alias_name=alias_name,
                    submission_file_path=tmp_submission_file,
                )
        else:
            assert (
                workflow_id_utils.obtain_workflow_id_using_alias(
                    alias_name=alias_name,
                    submission_file_path=tmp_submission_file,
                )
                == workflow_id
            )

    @pytest.mark.parametrize(
        "workflow_id, exists",
        [
            ["d689adec-c600-4e4b-be37-4e30e65848c7", True],
            ["d638sdfs-c355-427b-be24-75s5fs56fs5s", False],
        ],
    )
    def test_workflow_id_exists(
        self,
        workflow_id: str,
        tmp_submission_file: str,
        exists: bool,
    ):
        assert (
            workflow_id_utils.workflow_id_exists(
                workflow_id=workflow_id,
                submission_file=tmp_submission_file,
            )
            == exists
        )
