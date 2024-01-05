from cortex_shell.role import Options, Output, Role, ShellRole


class TestRole:
    def test_options_from_dict(self):
        data = {
            "api": "test_api",
            "model": "test_model",
            "temperature": 0.8,
            "top_probability": 0.9,
        }
        options = Options.from_dict(data)
        assert options.api == "test_api"
        assert options.model == "test_model"
        assert options.temperature == 0.8
        assert options.top_probability == 0.9

    def test_output_from_dict(self):
        data = {
            "stream": True,
            "formatted": False,
            "color": "blue",
            "theme": "dark",
        }
        output = Output.from_dict(data)
        assert output.stream is True
        assert output.formatted is False
        assert output.color == "blue"
        assert output.theme == "dark"

    def test_role_fill_from(self):
        options1 = Options(api="api1", model="model1")
        options2 = Options(temperature=0.7, top_probability=0.8)
        output1 = Output(stream=True, formatted=False)
        output2 = Output(color="blue", theme="dark")

        role1 = Role("role1", "description1", options1, output1)
        role2 = Role("role2", "description2", options2, output2)

        role1.fill_from(role2)

        assert role1.options.api == "api1"
        assert role1.options.model == "model1"
        assert role1.options.temperature == 0.7
        assert role1.options.top_probability == 0.8
        assert role1.output.stream is True
        assert role1.output.formatted is False
        assert role1.output.color == "blue"
        assert role1.output.theme == "dark"

    def test_shell_role_init(self):
        options = Options(api="test_api", model="test_model")
        output = Output(stream=True, formatted=False)

        shell_role = ShellRole("id1", "description1", True, options, output)

        assert shell_role.name == "id1"
        assert shell_role.description == "description1"
        assert shell_role.default_execute is True
        assert shell_role.options.api == "test_api"
        assert shell_role.options.model == "test_model"
        assert shell_role.output.stream is True
        assert shell_role.output.formatted is False
