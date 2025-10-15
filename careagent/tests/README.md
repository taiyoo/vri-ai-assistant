# Testing & Simulation Framework for Multi-Agent Orchestration Platform

This directory contains comprehensive testing tools for the multi-agent aged care voice documentation platform. The framework tests routing accuracy, Bedrock agent calls, discrepancy detection, and concurrency performance.

## 📁 Files Overview

### Core Testing Scripts

- **`run_tests.py`** - Main test runner that coordinates all testing activities
- **`simple_test.py`** - Standalone testing framework that works without complex dependencies
- **`test_simulation.py`** - Advanced simulation framework using synthetic ADL data
- **`load_test.py`** - Load testing for concurrent agent performance

### Utility Scripts

- **`README.md`** - This documentation file

## 🚀 Quick Start

### Prerequisites

1. Ensure you're in the `careagent/tests/` directory
2. Python 3.8+ installed
3. Synthetic ADL dataset available at `../../../adl_synthetic_dataset/`

### Running Tests

#### Option 1: Complete Test Suite
```bash
python run_tests.py --full
```

#### Option 2: Quick Validation
```bash
python run_tests.py --quick
```

#### Option 3: Load Testing Only
```bash
python run_tests.py --load --agents 2 --requests 20
```

#### Option 4: Direct Framework Testing
```bash
python simple_test.py --agents 2 --requests 10
```

## 📊 Test Categories

### 1. Routing Logic Tests
- Tests intent classification accuracy
- Validates routing decisions
- Measures confidence scores

### 2. Single Agent Performance
- Baseline performance metrics
- Response time analysis
- Success rate tracking

### 3. Multi-Agent Concurrency
- Concurrent request handling
- Throughput improvement analysis
- Resource utilization

### 4. Bedrock Agent Call Verification
- Tests all domain agents (ADL, Medication, Behavior, Governance)
- Token usage tracking
- Cost estimation
- Error handling

### 5. Discrepancy Detection
- Mock discrepancy scenarios
- Severity classification
- Resolution tracking
- Audit trail

### 6. Synthetic Data Analysis
- ADL scenario distribution
- Environment and role analysis
- Data quality assessment

## 📈 Metrics Collected

### Performance Metrics
- **Response Time**: Average time per request
- **Success Rate**: Percentage of successful requests
- **Throughput**: Requests per second
- **Concurrency Efficiency**: Multi-agent vs single-agent performance

### Routing Metrics
- **Accuracy**: Correct intent predictions
- **Confidence Scores**: Classification confidence
- **Intent Distribution**: Breakdown by category

### Bedrock Metrics
- **Token Usage**: Input/output tokens per call
- **Cost Estimates**: AWS Bedrock usage costs
- **Agent Utilization**: Calls per domain agent
- **Error Rates**: Failed Bedrock calls

### Discrepancy Metrics
- **Detection Rate**: Discrepancies found
- **Severity Distribution**: Low/Medium/High severity
- **Resolution Rate**: Resolved vs pending

## 📋 Test Scenarios

### Mock Voice Inputs
The framework includes realistic mock voice inputs across all intents:

**ADL Recording**: 
- "I need to record that Mrs. Johnson had a shower this morning"
- "Patient completed her breakfast and took her medications"

**Medication Management**:
- "What's the dosage for warfarin for this patient?"
- "Patient missed her morning medications"

**Behavioral Assessment**:
- "Patient was agitated during care this morning"
- "Resident seems confused and doesn't recognize staff"

**Governance/Compliance**:
- "Need to verify all ADL documentation is complete"
- "Check if medication administration was properly recorded"

### Synthetic Dataset Integration
When available, the framework uses the ADL synthetic dataset for:
- Realistic care scenarios
- Multi-turn dialogues
- Context-aware testing
- Diverse resident profiles

## 📊 Report Generation

All tests generate detailed reports in JSON format:

### Test Reports
- `test_report_YYYYMMDD_HHMMSS.json` - Detailed test execution results
- `test_execution_summary_YYYYMMDD_HHMMSS.json` - High-level summary

### Metrics Reports
- `metrics_routing_YYYYMMDD_HHMMSS.json` - Routing decision details
- `metrics_bedrock_YYYYMMDD_HHMMSS.json` - Bedrock call statistics
- `metrics_discrepancies_YYYYMMDD_HHMMSS.json` - Discrepancy detection logs
- `metrics_summary_YYYYMMDD_HHMMSS.json` - Overall metrics summary

## 🔧 Configuration

### Command Line Options

#### run_tests.py
```bash
--full          # Run complete test suite
--quick         # Run quick validation tests only
--load          # Run load tests only
--agents N      # Number of concurrent agents (default: 2)
--requests N    # Number of requests for testing (default: 20)
```

#### simple_test.py
```bash
--agents N      # Number of concurrent agents
--requests N    # Requests per agent
--data-path P   # Path to synthetic ADL data
```

### Test Parameters
You can customize test parameters by modifying the scripts:

- **Request Volume**: Adjust `requests_per_agent` for different load levels
- **Concurrency**: Modify `num_agents` for concurrency testing
- **Delays**: Change `delay_between_requests` for realistic timing
- **Intent Distribution**: Customize intent probability weights

## 🎯 Success Criteria

### Routing Verification
- ✅ Routing accuracy > 85%
- ✅ Average response time < 1.0s
- ✅ All intents properly classified

### Bedrock Agent Calls
- ✅ All domain agents respond successfully
- ✅ Token usage within expected ranges
- ✅ Error handling works correctly

### Discrepancy Detection
- ✅ Discrepancies are detected and logged
- ✅ Severity classification is accurate
- ✅ Audit trail is maintained

### Concurrency Performance
- ✅ Multi-agent throughput > single-agent
- ✅ Success rate maintained under load
- ✅ Resource utilization is efficient

## 🔍 Troubleshooting

### Common Issues

#### Import Errors
If you see import errors for `src` modules:
```bash
# Ensure you're in the correct directory
cd careagent/tests/

# Use the simple test framework which has fewer dependencies
python simple_test.py
```

#### Missing Synthetic Data
If synthetic data is not found:
```bash
# Check if the data exists
ls ../../../adl_synthetic_dataset/01_data/processed/

# Run without synthetic data (uses built-in mock data)
python simple_test.py --agents 1 --requests 5
```

#### Bedrock Connection Issues
If Bedrock agents fail to connect:
- Check AWS credentials
- Verify region configuration
- Ensure Bedrock models are accessible
- Use mock mode for testing logic

### Debug Mode
For detailed logging, modify the scripts to enable debug logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📈 Performance Benchmarks

### Expected Performance
Based on testing with mock data:

- **Single Agent**: ~5-10 requests/second
- **Dual Agents**: ~8-15 requests/second  
- **Success Rate**: >90%
- **Average Response Time**: 0.1-0.5 seconds (mock mode)

### Real Performance (with Bedrock)
Expected performance with actual Bedrock calls:

- **Single Agent**: ~1-3 requests/second
- **Dual Agents**: ~2-5 requests/second
- **Success Rate**: >95%
- **Average Response Time**: 0.5-2.0 seconds

## 🚀 Next Steps

1. **Run the complete test suite** to establish baseline metrics
2. **Analyze reports** to identify performance bottlenecks
3. **Scale testing** to more agents as needed
4. **Integrate with CI/CD** for automated testing
5. **Add custom test scenarios** for specific use cases

## 📞 Support

For questions or issues with the testing framework:
1. Check this README for common solutions
2. Review test output for specific error messages
3. Examine generated reports for detailed metrics
4. Modify test parameters to isolate issues
