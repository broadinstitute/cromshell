import json

import pytest

from cromshell.list_outputs import command as list_outputs_command


class TestListOutputs:
    """Test the execution list-outputs command functions"""

    @pytest.mark.parametrize(
        "workflow_metadata_file, outputs_metadata_file_path",
        [
            [
                "succeeded_helloworld.metadata.json",
                "list_outputs/succeeded_helloworld.outputs.metadata.json",
            ],
        ],
    )
    def test_filer_outputs_from_workflow_metadata(
        self,
        mock_data_path,
        tests_metadata_path,
        workflow_metadata_file,
        outputs_metadata_file_path,
    ):
        with open(tests_metadata_path.joinpath(workflow_metadata_file), "r") as f:
            workflow_metadata = json.load(f)

        with open(mock_data_path.joinpath(outputs_metadata_file_path), "r") as f:
            outputs_metadata = json.load(f)

        assert (
            list_outputs_command.filter_outputs_from_workflow_metadata(
                workflow_metadata
            )
            == outputs_metadata
        )

    @pytest.mark.parametrize(
        "outputs_metadata_file_path, expected_task_level_outputs_file_path",
        [
            [
                "list_outputs/succeeded_helloworld.outputs.metadata.json",
                "list_outputs/helloworld_task_level_outputs.txt",
            ],
        ],
    )
    def test_print_task_level_outputs(
        self,
        outputs_metadata_file_path: dict,
        mock_data_path,
        expected_task_level_outputs_file_path,
        capsys,
    ) -> None:
        """Test the print_task_level_outputs function"""

        with open(mock_data_path.joinpath(outputs_metadata_file_path), "r") as f:
            outputs_metadata = json.load(f)
        with open(
            mock_data_path.joinpath(expected_task_level_outputs_file_path), "r"
        ) as f:
            expected_task_level_outputs = f.read()

        list_outputs_command.print_task_level_outputs(outputs_metadata)

        captured = capsys.readouterr()
        assert captured.out == expected_task_level_outputs

    @pytest.mark.parametrize(
        "outputs_api_example_file, expected_workflow_level_outputs_file_path, indent",
        [
            [
                "list_outputs/helloworld_dict_of_outputs.json",
                "list_outputs/print_file_like_value_in_dict_example.txt",
                True,
            ],
            [
                "list_outputs/helloworld_dict_of_outputs.json",
                "list_outputs/print_file_like_value_in_dict_no_indent_example.txt",
                False,
            ],
        ],
    )
    def test_print_output_metadata(
        self,
        outputs_api_example_file,
        tests_metadata_path,
        mock_data_path,
        expected_workflow_level_outputs_file_path,
        indent,
        capsys,
    ) -> None:
        with open(mock_data_path.joinpath(outputs_api_example_file), "r") as f:
            outputs_metadata = json.load(f)
        with open(
            mock_data_path.joinpath(expected_workflow_level_outputs_file_path), "r"
        ) as f:
            expected_workflow_level_outputs = f.read()

        list_outputs_command.print_file_like_value_in_dict(
            outputs_metadata, indent=indent
        )

        captured = capsys.readouterr()
        assert captured.out == expected_workflow_level_outputs

    @pytest.mark.parametrize(
        "output_name, output_value, indent, expected_function_print",
        [
            [
                "task_name",
                "/taskoutputfile",
                True,
                "\ttask_name: /taskoutputfile\n",
            ],
            [
                "task_name",
                "taskoutputfile",
                True,
                "",
            ],
            [
                "task_name",
                "gs://taskoutputfile",
                True,
                "\ttask_name: gs://taskoutputfile\n",
            ],
        ],
    )
    def test_print_output_name_and_file(
        self,
        output_name,
        output_value,
        indent,
        expected_function_print,
        capsys,
    ) -> None:
        list_outputs_command.print_output_name_and_file(
            output_name=output_name,
            output_value=output_value,
            indent=indent,
        )

        captured = capsys.readouterr()
        assert captured.out == expected_function_print

    @pytest.mark.parametrize(
        "value, expected_bool",
        [
            [
                "task_value",
                False,
            ],
            [
                "/task_value",
                True,
            ],
            [
                "gs://task_value",
                True,
            ],
            [
                "task_value/",
                False,
            ],
            [
                "http://task_value",
                True,
            ],
        ],
    )
    def test_is_path_or_url_like(self, value, expected_bool):
        assert list_outputs_command.is_path_or_url_like(value) == expected_bool


    @pytest.mark.parametrize(
        "example_output_results, workflow_id",
        [
            [
                {'outputs': {}, 'id': '04b65be4-896f-439c-8a01-5e4dc6c116dd'},
                "04b65be4-896f-439c-8a01-5e4dc6c116dd'",
            ],
            [
                {'outputs': {"one": 2}, 'id': '04b65be4-896f-439c-8a01-5e4dc6c116dd'},
                "04b65be4-896f-439c-8a01-5e4dc6c116dd'",
            ],
        ],
    )
    def test_check_for_empty_output(
        self, example_output_results: dict, workflow_id: str
    ):
        """Test the check_for_empty_output function"""

        if example_output_results.get("outputs") == {}:
            with pytest.raises(Exception):
                list_outputs_command.check_for_empty_output(
                    example_output_results, workflow_id
                )
        else:
            assert (
                list_outputs_command.check_for_empty_output(
                    example_output_results, workflow_id
                ) is None
            )