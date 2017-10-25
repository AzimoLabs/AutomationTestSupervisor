# AutomationTestSupervisor
Python tool for launching and managing Android Virtual Devices and Android Automation Tests. It provides elastic configurations, test and launch profiles, test video recording, html log generation and more.

## Related Articles
- Story behind AutomationTestSupervisor — our custom made tool for Android automation tests

## Example Project
We are aware of that ATS has many functions and features. Some people prefer to see code rather then read blocks of text. That's why we have prepared example Android application - **AzimoNote** and wrote few Espresso tests so you can pull it and launch ATS by yourself.

In this example ATS is joined with **AzimoNote** in form of submodule. We use it the same way in Azimo project. It's quite convenient way as you can easily delegate ATS work to Jenkins or Gitlab. It is being downloaded along with Azimo repository and it's already pre-configured. You only need one CI command to launch it.

We have provided **Quick Launch** for you to follow.
- [Link to AzimoNote project](https://github.com/AzimoLabs/AzimoNote)

## Quick Launch
Meeting minimum launch requirements step by step:
1. Make sure you have Python 3.6 or newer installed and available from terminal. (If you are MAC OS user we highly recommend [Homebrew](https://brew.sh/index_pl.html) -> `brew install python3`.)
2. Clone AutomationTestSupervisor project to you machine from https://github.com/AzimoLabs/AutomationTestSupervisor.
3. Navigate to AutomationTestSupervisor folder on your machine.
4. Launch ATS with following command:
```
python3 Launcher.py
```

### Launch command parameters
It is possible to add four parameters to ATS launch command:
- pset < name of Path Module set >
- lplan < name of Launch Module launch plan >
- aset < name of AVD Module set >
- tset < name of Test Module set >

Parameters can be added in any order you like. If you omit some parameter ATS will try to look for set/plan with name `"default"` in manifest JSON files.

In example:
```
python3 Launcher.py -tset deeplinkTests -aset 3AVD-API23 -pset JenkinsPaths
```

## Module configurations
AutomationTestSupervisor can be divided into four main modules where each of them has it’s own config manifest file. Modules are integrated which each other and forming linear pipeline with set of steps. By modifying manifest of each module you can adjust behaviour of each step.

We wanted to make ATS project as self-contained as possible. That means we didn't wanted to force you to edit anything in the project. General idea is to just pull it and provide your own config files in right directory. In root of ATS project there is `config_files_dir.json` file which looks like this:
```
{
  "path_manifest_path": "../automationTestSupervisorConfig/pathManifest.json",
  "launch_manifest_path": "../automationTestSupervisorConfig/launchManifest.json",
  "test_manifest_path": "../automationTestSupervisorConfig/testManifest.json",
  "avd_manifest_path": "../automationTestSupervisorConfig/avdManifest.json"
}
```
It points for directory where you should put config .json files -> [This is how it looks in test project](https://github.com/AzimoLabs/AzimoNote/tree/master/automation).

(Templates for .json manifest files)[https://github.com/AzimoLabs/AutomationTestSupervisor/tree/master/settings/manifest/templates] are located in AutomationTestSupervisor project itself.

### Path Module
File pathManifest.json:
```

{
  "path_set_list": [
    {
      "set_name": "default",
      "paths": [
        {
          "path_name": "sdk_dir",
          "path_value": "",
          "path_description": "Path to Android Software Development kit. By default stored in ANDROID_HOME env."
        },
        {
          "path_name": "avd_dir",
          "path_value": "",
          "path_description": "Location to .android folder where AVD images are stored. By default stored in ANDROID_SDK_HOME env."
        },
        {
          "path_name": "output_dir",
          "path_value": "",
          "path_description": "Path to where test process logs will be saved. By default ./output/."
        },
        {
          "path_name": "project_root_dir",
          "path_value": "",
          "path_description": "Path to root of application under test. (optional)"
        },
        {
          "path_name": "apk_dir",
          "path_value": "",
          "path_description": "Directory where .apk files of application under test are stored."
        }
      ]
    }
  ]
}
```
Overview:
- You can provide both relative and absolute paths. ATS will convert relative paths to absolute paths anyway.
- You can provide many set of paths (for different machines/developers) by adding another object `path_set_list` and giving it unique `set_name`.

Parameters (explanations in `path_description`):
- **`sdk_dir`**
- **`avd_dir`**
- **`output_dir`**
- **`project_root_dir`** - If you want to allow ATS to build .apk files of your project then you need to provide path to it so ATS can access `./gradlew` file.
- **`apk_dir`** - Directory where ATS will look for .apk files. If it won't find them and `project_root_dir` is properly set then there is a possibility to build them.

### Launch Module
File: launchManifest.json
```
{
  "launch_plan_list": [
    {
      "plan_name": "default",
      "general": {
        "adb_call_buffer_size": 3,
        "adb_call_buffer_delay_between_cmd": 2000
      },
      "device_preparation_phase": {
        "avd_should_recreate_existing": true
      },
      "apk_preparation_phase": {
        "build_new_apk": true
      },
      "device_launching_phase": {
        "device_android_id_to_ignore": [],
        "avd_launch_sequentially": true,
        "avd_status_scan_interval_millis": 10000,
        "avd_wait_for_adb_boot_timeout_millis": 240000,
        "avd_wait_for_system_boot_timeout_millis": 120000,
        "device_before_launching_restart_adb": true
      },
      "testing_phase": {
        "record_tests": true
      }
    }
  ]
}
```
Overview:
- You can create many launch plans by adding another object `launch_plan_list` and giving it unique `plan_name`.
- Check how it's done in `AzimoNote` project -> [link](https://github.com/AzimoLabs/AzimoNote/blob/master/automation/automationTestSupervisorConfig/avdManifest.json)

Parameters:
- ADB Buffer - as ADB has problem with too frequent calls to it and tends to process information too slow and return errors. Unfortunately it's limitation of ADB and all you can do is to wait for some major improvement/update. So to avoid spamming it, every command to ADB is entering buffer of size **`adb_call_buffer_size`** and then it's released after **`adb_call_buffer_delay_between_cmd`** milliseconds. This will allow you to reduce burden on your ADB in case you used weaker machine or decided to run tons of AVD.
- **`avd_should_recreate_existing`** - Boolean value, if AVD that you have picked for your session already exists on your machine you can either choose to leave them as they are or ask ATS to re-create them (to completely reset memory state of device for example)
- **`build_new_apk`** - If ATS won't find your .apk in directory specified in PathModule it will attempt to build it if you wish for that. In some cases you are debugging your tests and try to run it many times to trigger some non-deterministic action. That's why you don't want to wait for .apk being built from scratch every time if you are not making any changes to your code. If you are 100% sure .apk is already built you can use this flag to create "speed-run" launch plan.
- **`device_android_id_to_ignore`** - Simply enter Android Device Id that should be ignored.
- **`avd_launch_sequentially`** - After you've requested list of AVD to launch you can either wait for their boot in parallel or "one by one". Though non-sequential launch is dangerous for your OS. What's limiting how many AVD can be launched at the same time is HAXM. If you run 10 AVD in exactly same moment (where each takes ~1GB of RAM) - even though limit of your HAXM might be 6GB of RAM - SDK won't stop you from doing that. It will perform 10 checks and each of them will say - there is 6GB of free RAM, go ahead. That way you can launch more AVD - over the limit of your HAXM and in worst case you will crash your OS with out of memory error.
- **`avd_status_scan_interval_millis`** - When AVD is booting and ATS is waiting for it this parameter allows you to set interval (millis) in which ADB will check device state.
- **`avd_wait_for_adb_boot_timeout_millis`** - Timeout for so called `ADB BOOT`. It's time from launching terminal command that should start AVD to moment where ADB will display AVD in `adb list` with status `device`. At that point system of AVD just started booting.
- **`avd_wait_for_system_boot_timeout_millis`** - Wait for system parameters of AVD
- **`device_before_launching_restart_adb`** - You can choose if ADB should be restarted before it starts working with AVD.
- **`record_tests`** - You can choose if every test should be recorded. It will put more burden on your machine.

### AVD Module
File: avdManifest.json
```
{
  "avd_schema_list": [
    {
      "avd_name": "",
      "create_avd_package": "",
      "create_device": "",
      "create_avd_tag": "",
      "create_avd_abi": "",
      "create_avd_additional_options": "",
      "create_avd_hardware_config_filepath": "",
      "launch_avd_snapshot_filepath": "",
      "launch_avd_launch_binary_name": "",
      "launch_avd_additional_options": ""
    }
  ],
  "avd_set_list": [
    {
      "set_name": "default",
      "avd_list": [
        {
          "avd_name": "",
          "instances": -1
        }
      ],
      "avd_port_rules": {
        "assign_missing_ports": true,
        "search_range_min": 5556,
        "search_range_max": 5580,
        "ports_to_ignore": [],
        "ports_to_use": []
      }
    }
  ]
}
```
Overview:
- You can create many AVD schemas in `avd_schema_list` which can be then used to create sets in `avd_set_list`.
- Check how it's done in `AzimoNote` project -> [link](https://github.com/AzimoLabs/AzimoNote/blob/master/automation/automationTestSupervisorConfig/avdManifest.json)

If you were user of our [fastlane-emulator-run-plugin](https://github.com/AzimoLabs/fastlane-plugin-automated-test-emulator-run) than you can notice that this way of created AVD for test session is actually very similar adopted mechanism with some extensions.

AVD schema parameters:
- **`avd_name`** - Name of your AVD, avoid using spaces, this field is necessary.
- **`create_avd_package`** - Path to system image eg. "system-images;android-23;google_apis;x86_64".
- **`create_device`** - Name of your device visible on `avdmanager list`.
- **`create_avd_tag`** - The sys-img tag to use for the AVD. e.g. if you are using Google Apis then set it to "google_apis".
- **`create_avd_abi`** - Abi for AVD e.g. "x86" or "x86_64" (https://developer.android.com/ndk/guides/abis.html).
- **`create_avd_additional_options`** - If you think that you need something more you can just add your create parameters here (e.g. "--sdcard 128M".
- **`create_avd_hardware_config_filepath`** - Path to config.ini file containing custom config for your AVD. After AVD is created this file will be copied into AVD location before it launches.
- **`launch_avd_snapshot_filepath`** - Plugin might (if you set it) delete and re-create AVD before test start. That means all your permissions and settings will be lost on each emulator run. If you want to apply QEMU image with saved AVD state you can put path to it in this field. It will be applied by using `-wipe-data -initdata` command.
- **`launch_avd_launch_binary_name`** -Ddepending on your CPU architecture you need to choose binary file which should launch your AVD (e.g. "emulator", "emulator64-arm").
- **`launch_avd_additional_options`** - If you need more customization add your parameters here (e.g. "-gpu on -no-boot-anim -no-window", https://developer.android.com/studio/run/emulator-commandline.html)

AVD set parameters:
- **`avd_list`** - List of .json objects where names of AVD schemas can be listed and quantity of emulator that should be launched from them.
- **`assign_missing_ports`** - ATS will pick free ports automatically for you if this flag is set to true, otherwise it will use port list provided by you.
- **`search_range_min`** - Value from which ATS starts too look for free ports. Google recommended to use ports 5556 - 5580.
- **`search_range_max`** - Value from which ATS stops too look for free ports.
- **`ports_to_ignore`** - In case you had port reserved for something you can ask ATS to omit it.
- **`ports_to_use`** - Your own list of ports to use. Remember to pick only even ports as uneven ones are reserved for ADB instances cooperating with AVD instance (e.g. if you pick 5554 then 5555 will be used by ADB).

### Test Module
File testManifest.json:
```
{
  "test_list": [
    {
      "test_package_name": "",
      "test_packages": [],
      "test_classes": [],
      "test_cases": []
    }
  ],
  "test_set_list": [
    {
      "set_name": "default",
      "apk_name_part": "",
      "application_apk_assemble_task": "",
      "test_apk_assemble_task": "",
      "gradle_build_params": "",
      "shard": false,
      "set_package_names": []
    }
  ]
}
```
Overview:
- You HAVE TO create list of your test packages in `test_list`. Package is a java-package to folder where .java files with @Test annotated code.
- Check how it's done in `AzimoNote` project -> [link](https://github.com/AzimoLabs/AzimoNote/blob/master/automation/automationTestSupervisorConfig/testManifest.json)

![](git_images/test_package_example.png =411×445)

For example this is a package with 4 test containers:
- SearchContact_AllContacts_Tests
- SearchContact_AzimoInstant_Tests
- SearchContact_MyRecipients_Tests
- SearchContact_NewUser_Tests

Which are inside package `com.azimo.sendmoney.instrumentation.azimoTestCases.bddTests.functional.SearchContact`. Example test package object could look like this (you pick `test_package_name` to your liking):
```
{
  "test_package_name": "SearchContactTests",
  "test_packages": [
    com.azimo.sendmoney.instrumentation.azimoTestCases.bddTests.functional.SearchContact
  ],
  "test_classes": [],
  "test_cases": []
}
```

#### Important:
Parameters `test_classes` and `test_cases` are not supported for now.

Test set parameters:
- **`apk_name_part`** - Part of .apk name. ATS will look for .apk files containing this name in specified in Path Module directory. From all .apk files that contains this "name part" it will pick those which has highest version code and both application and test .apk files exists.
- **`application_apk_assemble_task`** - Gradle task for building application .apk. You can create ATS sets for different flavours.
- **`test_apk_assemble_task`** - Gradle task for building test .apk corresponding to .apk in `application_apk_assemble_task`.
- **`gradle_build_params`** - Gradle parameters which you can add to .apk build process.
- **`shard`** - Boolean value. Based on this flag you can decide if tests will run in parallel on each device or will be divided into parts (called shards) where each device will receive only part of tests.
- **`set_package_names`** - If you have finished filling up your `test_list` then you have many test package objects here, where each object has `test_package_name`. **`set_package_names`** is a list for those `test_package_name` values.

### AutomationTestSupervisor features
1. Logging
  a) HTML dashboard generation - ATS provides you with fully generated HTML website structure where you can preview your test session. It contains:
    - General test health rate.
    - List of failed tests.
    - List of module sets/plan you have used in this session.
    - Used .apk name, version, build time.
    - Device creation, boot, time, .apk install time.
    - Expandable list of test packages with test cases and their status.
    - Highlighted error of test.
    - Test duration.
    - Device on which test ran.
    - Link to LogCat from test session (another generated and pre-formatted HTML page).
    - Link to videos from test (if feature was used).
  b) Logs from tests in form of JSON files.
  c) Logs from emulators.

### Possible new features
a) AutomationTestSupervisor
  - Support for ADB Orchistrator (HOT).
  - Possibility to re-run failed tests to flag flakiness.
  - 3x retry with small time interval on ADB commands as it tends to malfunctions (rarely but still).
  - Screenshots - This function was not implemented as it cannot be done from Python code. We could take random screenshots from terminal but best performance is when user can specify in test when screenshot should be taken. It requires some universal java class for taking screenshots and additionally supports for real-time screenshot pulling from devices. In general it's much work to do it properly.
  - Add list parameter to display currently available manifest configs.

b) LauncherWizard - subtool
  - Wizard version of launcher that leads person which doesn't know how to start test with usage of single command. Wizard will show possible options and react to user answers.

c) LauncherConfigCreator - subtool
  - Tool that will ask user to fill all necessary fields by question/answer format. After process is finished user will receive manifest file configs compatible with his machine.

### Problems to be solved
a) Test recording is working but the way files are pulled from device is very imperfect. This is due to fact, even if you stop recording from terminal command ADB still takes few seconds to process file. If you pull video too fast then it will be corrupted and won't run. This is simply bug in ADB as it doesn't release video recording process in the moment when video is ready to use. We tested this feature on our test set (where some tests take even 6 minutes) and decided to wait 10 seconds before each file is pulled. This will cause huge problem if someone has set of very small and fast tests. What needs to be done to **implement proper synchronisation/wait for .mp4 to finish being written to** in [TestRecordingSavingThread](https://github.com/AzimoLabs/AutomationTestSupervisor/blob/master/session/SessionThreads.py).
