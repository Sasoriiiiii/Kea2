
# Documentation

[中文文档](manual_cn.md)

## Kea2's tutorials 

1. A small tutorial of applying Kea2's Feature 2 and 3 on [WeChat](Scenario_Examples_zh.md).

## Kea2's scripts

Kea2 uses [Unittest](https://docs.python.org/3/library/unittest.html) to manage scripts. All the Kea2's scripts can be found in unittest's rules (i.e., the test methods should start with `test_`, the test classes should extend `unittest.TestCase`).

Kea2 uses [Uiautomator2](https://github.com/openatx/uiautomator2) to manipulate android devices. Refer to [Uiautomator2's docs](https://github.com/openatx/uiautomator2?tab=readme-ov-file#quick-start) for more details. 

Basically, you can write Kea2's scripts by following two steps:

1. Create a test class which extends `unittest.TestCase`. 

```python
import unittest 

class MyFirstTest(unittest.TestCase):
    ...
```

2. Write your own script by defining test methods

By default, only the test method starts with `test_` will be found by unittest. You can decorate the function with `@precondition`. The decorator `@precondition` takes a function which returns boolean as an arugment. When the function returns `True`, the precondition is satisified and the script will be activated, and Kea2 will run the script based on certain probability defined by the decorator `@prob`.

Note that if a test method is not decorated with `@precondition`.
This test method will never be activated during automated UI testing, and will be treated as a normal `unittset` test method.
Thus, you need to explicitly specify `@precondition(lambda self: True)` when the test method should be always executed. When a test method is not decorated with `@prob`, the default probability is 1 (always execute when precondition satisfied). 

```python
import unittest
from kea2 import precondition

class MyFirstTest(unittest.TestCase):

    @prob(0.7)
    @precondition(lambda self: ...)
    def test_func1(self):
        ...
```

You can read [Kea - Write your fisrt property](https://kea-docs.readthedocs.io/en/latest/part-keaUserManuel/first_property.html) for more details.

## Decorators 

### `@precondition`

```python
@precondition(lambda self: ...)
def test_func1(self):
    ...
```

The decorator `@precondition` takes a function which returns boolean as an arugment. When the function returns `True`, the precondition is satisified and function `test_func1` will be activated, and Kea2 will run `test_func1` based on certain probability value defined by the decorator `@prob`.
The default probability value is 1 if `@prob` is not specified. In this case, function `test_func1` will be always executed when its precondition is satisfied.

### `@prob`

```python
@prob(0.7)
@precondition(lambda self: ...)
def test_func1(self):
    ...
```

The decorator `@prob` takes a float number as an argument. The number represents the probability of executing function `test_func1` when its precondition (specified by `@precondition`) is satisfied. The probability value should be between 0 and 1. 
The default probability value is 1 if `@prob` is not specified. In this case, function `test_func1` will be always executed when its precondition is satisfied.

When the preconditions of multiple functions are satisfied. Kea2 will randomly select one of these functions to execute based on their probability values. 
Specifically, Kea2 will generate a random value `p` between 0 and 1, and `p` will be used to decide which function to be selected based on the probability values of
these functions.

For example, if three functions `test_func1`, `test_func2` and `test_func3` whose preconditions are satisified, and
their probability values are `0.2`, `0.4`, and `0.6`, respectively. 
- Case 1: If `p` is randomly assigned as `0.3`, `test_func1` will lose the chance of being selected because its probability value `0.2` is smaller than `p`. Kea2 will *randomly* select one function from `test_func2` and `test_func3` to be executed.
- Case 2: If `p` is randomly assigned as `0.1`, Kea2 will *randomly* select one function from `test_func1`, `test_func2` and `test_func3` to be executed.
- Case 3: If `p` is randomly assigned as `0.7`, Kea2 will ignore all these three functions `test_func1`, `test_func2` and `test_func3`.


### `@max_tries`

```python
@max_tries(1)
@precondition(lambda self: ...)
def test_func1(self):
    ...
```

The decorator `@max_tries` takes an integer as an argument. The number represents the maximum number of times function `test_func1` will be executed when the precondition is satisfied. The default value is `inf` (infinite).


## Launching Kea2

We offer two ways to launch Kea2.

### 1. Launch by shell commands

Kea2 is compatible with `unittest` framework. You can manage your test cases in unittest style. You can launch Kea2 with `kea run` with driver options and sub-command `unittest` (for unittest options).

The shell command:
```
kea2 run <Kea2 cmds> unittest <unittest cmds> 
```

Sample shell commands:

```bash
# Launch Kea2 and load one single script quicktest.py.
kea2 run -s "emulator-5554" -p it.feio.android.omninotes.alpha --agent u2 --running-minutes 10 --throttle 200 --driver-name d unittest discover -p quicktest.py

# Launch Kea2 and load multiple scripts from the directory mytests/omni_notes
kea2 run -s "emulator-5554" -p it.feio.android.omninotes.alpha --agent u2 --running-minutes 10 --throttle 200 --driver-name d unittest discover -s mytests/omni_notes -p test*.py
```

If you need to pass extra arguments to the underlying Fastbot, append `--` after the regular arguments, then list the extra arguments. For example, to set the touch event percentage to 30%, run:

```bash
kea2 run -s "emulator-5554" -p it.feio.android.omninotes.alpha --agent u2 --running-minutes 10 --throttle 200 --driver-name d -- --pct-touch 30 unittest discover -p quicktest.py
```

### `kea2 run` Options

| arg | meaning | default | 
| --- | --- | --- |
| -s | The serial of your device, which can be found by `adb devices` | |
| -t | The transport id of your device, which can be found by `adb devices -l` | |
| -p | Specify the target app package name(s) to test (e.g., com.example.app). *Supports multiple packages: `-p pkg1 pkg2 pkg3`* | 
| -o | The ouput directory for logs and results | `output` |
| --agent |  {native, u2}. By default, `u2` is used and supports all the three important features of Kea2. If you hope to run the orignal Fastbot, please use `native`.| `u2` |
| --running-minutes | The time (in minutes) to run Kea2 | `10` |
| --max-step | The maxium number of monkey events to send (only available in `--agent u2`) | `inf` (infinite) |
| --throttle | The delay time (in milliseconds) between two monkey events | `200` |
| --driver-name | The name of driver used in the kea2's scripts. If `--driver-name d` is specified, you should use `d` to interact with a device, e..g, `self.d(..).click()`. |
| --log-stamp | the stamp for log file and result file. (e.g., if `--log-stamp 123` is specified, the log files will be named as `fastbot_123.log` and `result_123.json`.) | current time stamp |
| --profile-period | The period (in the numbers of monkey events) to profile coverage and collect UI screenshots. Specifically, the UI screenshots are stored on the SDcard of the mobile device, and thus you need to set an appropriate value according to the available device storage. | `25` |
| --take-screenshots | Take the UI screenshot at every Monkey event. The screenshots will be automatically pulled from the mobile device to your host machine periodically (the period is specified by `--profile-period`). |  |
| --device-output-root | The root of device output dir. Kea2 will temporarily save the screenshots and result log into `"<device-output-root>/output_*********/"`. Make sure the root dir can be access. | `/sdcard` |
| unittest | Specify to load which scripts. This  sub-command `unittest` is fully compatible with unittest. See `python3 -m unittest -h` for more options of unittest. This option is only available in `--agent u2`.


### `kea2 report` Options

The `kea2 report` command generates an HTML test report from existing test results. This command analyzes test data and creates a comprehensive visual report showing test execution statistics, coverage information, property violations, and crash details.

| arg | meaning | required | default |
| --- | --- | --- | --- |
| -p, --path | Path to the directory containing test results (res_* directory) | Yes | |

**Usage Examples:**

```bash
# Generate report from a test result directory
kea2 report -p res_20240101_120000

# Generate report with debug mode enabled
kea2 -d report -p res_20240101_120000

# Generate report using relative path
kea2 report -p ./output/res_20240101_120000
```

**What the report includes:**
- **Test Summary**: Total bugs found, execution time, coverage percentage
- **Property Test Results**: Execution statistics for each test property (preconditions satisfied, executed, failed, errors)
- **Code Coverage**: Activity coverage trends and detailed coverage information
- **Property Violations**: Detailed information about failed test properties with error traces
- **Crash Events**: Application crashes detected during testing
- **ANR Events**: Application Not Responding events
- **Screenshots**: UI screenshots captured during testing (if enabled)
- **Activity Traversal**: History of activities visited during testing

**Output:**
The report command generates:
- An HTML report file (`bug_report.html`) in the specified test result directory
- Interactive charts and visualizations for coverage and execution trends
- Detailed error information with stack traces for debugging

**Input Directory Structure:**
The command expects a test result directory with the following structure:
```
res_<timestamp>/
├── result_<timestamp>.json          # Property test results
├── output_<timestamp>/
│   ├── steps.log                    # Test execution steps
│   ├── coverage.log                 # Coverage data
│   ├── crash-dump.log               # Crash and ANR events
│   └── screenshots/                 # UI screenshots (if enabled)
└── property_exec_info_<timestamp>.json  # Property execution details
```

### `kea2 merge` Options

The `kea2 merge` command allows you to merge multiple test report directories and generate a combined report. This is useful when you have run multiple test sessions and want to consolidate the results into a single comprehensive report.

| arg | meaning | required | default |
| --- | --- | --- | --- |
| -p, --paths | Paths to test report directories (res_* directories) to merge. At least 2 paths are required. | Yes | |
| -o, --output | Output directory for merged report | No | `merged_report_<timestamp>` |

**Usage Examples:**

```bash
# Merge two test report directories
kea2 merge -p res_20240101_120000 res_20240102_130000

# Merge multiple test report directories with custom output
kea2 merge -p res_20240101_120000 res_20240102_130000 res_20240103_140000 -o my_merged_report

# Enable debug mode while merging
kea2 -d merge -p res_20240101_120000 res_20240102_130000
```

**What gets merged:**
- Property test execution statistics (preconditions satisfied, executed, failed, errors)
- Code coverage data (activities covered, coverage percentage)
- Crash and ANR events
- Test execution steps and timing information

**Output:**
The merge command generates:
- A merged report directory containing consolidated data
- An HTML report (`merged_report.html`) with visual summaries
- Merge metadata including source directories and timestamp

### `kea` options

| arg | meaning | default |
| --- | --- | --- |
| -d | Enable debug mode | |

> ```bash
> # add -d to enable debug mode
> kea2 -d run -s "emulator-5554" -p it.feio.android.omninotes.alpha --agent u2 --running-minutes 10 --throttle 200 --driver-name d unittest discover -p quicktest.py
> ```

### 2. Launch by `unittest.main`

Like unittest, we can launch Kea2 through the method `unittest.main`.

Here is an example (named as `mytest.py`). You can see that the options are directly defined in the script.

```python
import unittest

from kea2 import KeaTestRunner, Options
from kea2.u2Driver import U2Driver

class MyTest(unittest.TestCase):
    ...
    # <your test methods here>

if __name__ == "__main__":
    KeaTestRunner.setOptions(
        Options(
            driverName="d",
            Driver=U2Driver,
            packageNames=[PACKAGE_NAME],
            # serial="emulator-5554",   # specify the serial
            maxStep=100,
            # running_mins=10,  # specify the maximal running time in minutes, default value is 10m
            # throttle=200,   # specify the throttle in milliseconds, default value is 200ms
            # agent='native'  # 'native' for running the vanilla Fastbot
        )
    )
    # Declare the KeaTestRunner
    unittest.main(testRunner=KeaTestRunner)
```

We can directly run the script `mytest.py` to launch Kea2, e.g.,
```python
python3 mytest.py
```

Here's all the available options in `Options`.

```python
# the driver_name in script (if self.d, then d.) 
driverName: str
# the driver (only U2Driver available now)
Driver: U2Driver
# list of package names. Specify the apps under test
packageNames: List[str]
# target device
serial: str = None
# test agent. "u2" is the default agent
agent: "u2" | "native" = "u2"
# max step in exploration (availble in stage 2~3)
maxStep: int # default "inf"
# time(mins) for exploration
running_mins: int = 10
# time(ms) to wait when exploring the app
throttle: int = 200
# the output_dir for saving logs and results
output_dir: str = "output"
# the stamp for log file and result file, default: current time stamp
log_stamp: str = None
# the profiling period to get the coverage result.
profile_period: int = 25
# take screenshots for every step
take_screenshots: bool = False
# The root of output dir on device
device_output_root: str = "/sdcard"
# the debug mode
debug: bool = False
```

## Examining the running statistics of scripts .

If you want to examine whether your scripts have been executed or how many times they have been executed during testing. Open the file `result.json` after the testing is finished.

Here's an example.

```json
{
    "test_goToPrivacy": {
        "precond_satisfied": 8,
        "executed": 2,
        "fail": 0,
        "error": 1
    },
    ...
}
```

**How to read `result.json`**

Field | Description | Meaning
--- | --- | --- |
precond_satisfied | During exploration, how many times has the test method's precondition been satisfied? | Does we reach the state during exploration? 
executed | During UI testing, how many times the test method has been executed? | Has the test method ever been executed?
fail | How many times did the test method fail the assertions during UI testing? | When failed, the test method found a likely functional bug. 
error | How many times does the test method abort during UI tsting due to some unexpected errors (e.g. some UI widgets used in the test method cannot be found) | When some error happens, the script needs to be updated/fixed because the script leads to some unexpected errors.

## Configuration File

After executing `Kea2 init`, some configuration files will be generated in the `configs` directory. 
These configuration files belong to `Fastbot`, and their specific introductions are provided in [Introduction to configuration files](https://github.com/bytedance/Fastbot_Android/blob/main/handbook-cn.md#%E4%B8%93%E5%AE%B6%E7%B3%BB%E7%BB%9F).

## App's Crash Bugs
Kea2 dumps the triggered crash bugs in the `fastbot_*.log` generated in the output directory specified by `-o`. You can search the keyword `FATAL EXCEPTION` in `fastbot_*.log` to find the concrete information of crash bugs.

These crash bugs are also recorded on your device. [See the Fastbot manual for details](https://github.com/bytedance/Fastbot_Android/blob/main/handbook-cn.md#%E7%BB%93%E6%9E%9C%E8%AF%B4%E6%98%8E).
