# MAGPIE Platform Tests

This folder contains test scripts for validating the MAGPIE platform functionality.

## Test Files

- **[test_agents_functionality.py](test_agents_functionality.py)** - Test agent functionality and integration
- **[test_deepseek_integration.py](test_deepseek_integration.py)** - Test DeepSeek model integration
- **[test_engineering_process_procedure_agent.py](test_engineering_process_procedure_agent.py)** - Test engineering process agent
- **[test_multi_agent_models.py](test_multi_agent_models.py)** - Test multi-model implementation
- **[validate_multi_model_config.py](validate_multi_model_config.py)** - Validate multi-model configuration
- **[test_requirements.txt](test_requirements.txt)** - Additional test dependencies

## Running Tests

From the project root directory:

```bash
# Test multi-model configuration
python tests/validate_multi_model_config.py

# Test DeepSeek integration
python tests/test_deepseek_integration.py

# Test agent functionality
python tests/test_agents_functionality.py

# Test multi-agent models
python tests/test_multi_agent_models.py

# Test engineering process agent
python tests/test_engineering_process_procedure_agent.py
```

## Test Dependencies

Install additional test dependencies:
```bash
pip install -r tests/test_requirements.txt
```
