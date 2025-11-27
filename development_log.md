This document chronicles the development history of voxMate, a Python-based AI smart speaker for Raspberry Pi 4. Sessions are grouped by time gaps of 6+ hours between commits, representing distinct development periods.

--- 
<br>

## Session 28 
### Tuesday November 26th
<br>

**Summary:** This session focused on migrating from porcupine to openwakeword library for wake word detection, including debugging model initialization, fixing syntax errors, and adding documentation files. 

**Git Branch:** openwakeword<br>
**Git commits:**<br>
05b16ddc74e1e1b2dbd2fd65f24eb9ada3785ee3, 8d0871e36f60ab770e76585be92b0c0f89e64eb, ce992ea6aa8e9b57391e100b0879f69e22c985fa, 93e6d6bddf39f10c2089ab7948d4c0989ad81662,4120550eaa4c1d97491bd9949c1b329fc8d261a3, 5b424bffccbc5790609fb568f8709b7a870fc077, dbcad64a44265c2fb46b66b23f5dbfa14850387c, b88a426f867114b1380ca93c75c238bd0aaea268, 6149bddc7e9a84df26dff0000e7f095296d2931b, 28757280576c410d7a6ad32d0740d29297178c39, 26739502b43bee926870dd07695f0800127fb322, fa3de3a40bfbf23a4ba670133beb8e3f13a99779, 9c1c59f0e5b424ffc974e61870eeaab5d394f533, 1b39d56fac35c2a3b9ca50f10ae0d477357fd7f8, e809fda37602031fd2ab25578a6b0557618eeda2, 0774104494132a40aa00f49500df42f2604345e5, e3fe247df8a5683203040cd1532818c993b19106, def2a6f89f6ed42536151bb4600dcf658429b9f1, d96417b83f35b333074851f1c6a58cba74c094ee 

**Session git history:** 
- change porcupine to openwakeword - *Replaced porcupine wake word detection with openwakeword library*
- add openwakeword to requirements - *Updated requirements.txt to include openwakeword dependency*
- add models for openwakeword - *Added ONNX model files for wake word detection*
- debug openwakeword models - *Fixed model loading and path issues*
- debug openwakeword init - *Resolved initialization problems with openwakeword*
- debug openwakeword - *General debugging of openwakeword implementation*
- fix typo - *Corrected typo in code*
- debug oww model label - *Fixed model label detection issues*
- update oww model import - *Updated model import statements*
- debug oww model - *Continued model debugging*
- fix syntax error in oww - *Corrected syntax error in openwakeword code*
- debug str error in oww - *Fixed string type conversion error*
- change oww wake word - *Modified wake word detection parameters*
- debug no dection in oww - *Investigated wake word detection failure*
- change wake word name - *Updated wake word name/identifier*
- refactor: add docs dir and todo file - *Added documentation directory and TODO file*
- debug onnx warning - *Resolved ONNX runtime warnings*
- add connectmanager to suppress onnx warnings - *Implemented warning suppression for ONNX*
- update logger - *Updated logging configuration*
---
<br>

## Session 27 
### Monday November 25th
<br>

**Summary:** This session involved updating remote/local logic for voxMate operation, adding debugging capabilities, and preparing for openwakeword migration. 

**Git Branch:** main <br>
**Git commits:** <br>
e3163d65202c49d40fc085e33399ee934e60ae24, 212965bc8c77825e0e9308e52def7010f081c572 

**Session git history:** 
- update remote/local logic - *Updated logic for determining remote vs local operation*
- debug remote/local logic - *Added debugging for remote/local detection logic*
---
<br>

## Session 26 
### Sunday August 11th
<br>

**Summary:** This session focused on code refactoring by adding type hints to all functions and implementing remote working functionality for voxMate. 

**Git Branch:** thread_managment <br>
**Git commits:** <br>
531420a13a448ab6cb96788319073de1cf996a2c, 5cdd964265c0cd3ca38137f8c8a89472782fffa9 

**Session git history:** 
- refactor: add type hints to all functions - *Added comprehensive type hints across codebase*
- Add remote working function - *Implemented functionality for remote operation*
---
<br>

## Session 25
### Saturday August 10th
<br>

**Summary:** This session added Spotify news handler functionality and cleaned up imports in dispatcher module. 

**Git Branch:** radio <br>
**Git commits:** <br>
fc03b69ee768edbbc6fda88b6f55c2e75b0376d5, d5966107b2acd52a5158079e80263fd4852df1cb 

**Session git history:** 
- Add Spotify news handler - *Implemented news playback through Spotify*
- Remove get_news import from dispatcher - *Cleaned up unused imports*
---
<br>

## Session 24
### Friday August 9th
<br>

**Summary:** This session focused on updating run and stop scripts, testing Spotify stop functionality, and ensuring proper cleanup. 

**Git Branch:** main <br>
**Git commits:** <br>
9ed5b68fac09720031a8085f217a6eb05e5ead9e, 53d64f7c7974bbfd442f6cb08935abfddb4b2bc7, fa43b6fc2b293d987fcebc6f5ffff84a6837268b 

**Session git history:** 
- Update run and stop scripts - *Improved voxMate startup and shutdown scripts*
- Test Spotify stop - *Tested Spotify playback stopping functionality*
- Re-test spotify stop - *Additional testing of Spotify stop feature*
---
<br>

## Session 23 
### Tuesday August 6th
<br>

**Summary:** This session involved refactoring Spotify service and adding Spotify news podcast functionality to enhance music and news features. 

**Git Branch:** main <br>
**Git commits:** <br>
bb2527720db079726b4f7b0e95eb54c48deafe5a 

**Session git history:** 
- Refactored Spotify Service, Add spotify news podcast - *Restructured Spotify service and added news podcast capability*
---
<br>

## Session 22 
### Monday August 5th
<br>

**Summary:** This session added news RSS feed functionality, improved volume control handling for both string and integer inputs, and optimized Spotify startup volume. 

**Git Branch:** volume_control <br>
**Git commits:** <br>
1cac97cfe5857f12241c65eb2df24f52334ab4d6, 0ca7b6b0977f65efdaeb83cfb1fb8433165f8289, f757b029738e2c03b82b3e4cfe97928269d82bff, 72cbd2c44641c360ff39ec8dcb4d3339f1bb9fd6, 48fd9bb03c46892b6a51ebba0bc9e68b9df950c5 

**Session git history:** 
- Add news rss feed - *Implemented RSS news feed functionality*
- Fix typo - *Corrected typo in code*
- Add handling of str and int volume control - *Enhanced volume control to handle different data types*
- Update volume function - *Improved volume control implementation*
- Update spotify to start at 100% volume - *Set Spotify to start at maximum volume*
---
<br>

## Session 21 
### Friday August 2nd
<br>

**Summary:** This session added default volume settings to both startup and web application, improving user experience with consistent volume levels. 

**Git Branch:** main <br>
**Git commits:** <br>
a58a7533a597843fb498bcc27b71d5220b2f60e2 

**Session git history:** 
- Add deafult volume to startup and web app - *Implemented default volume settings*
---
<br>

## Session 20 
### Thursday August 1st
<br>

**Summary:** This session enhanced volume control by adding maximum and minimum volume limits to prevent audio issues and improve user control. 

**Git Branch:** main <br>
**Git commits:** <br>
2c46ecd84a2beecb072df33ba1659f69eeab8a4e 

**Session git history:** 
- Add max and min to volume - *Added volume range limits*
---
<br>


## Session 19 
### Wednesday July 31st
<br>

**Summary:** This session implemented comprehensive volume control features including up, down, and value controls, along with shuffle functionality and error handling improvements. 

**Git Branch:** main <br>
**Git commits:** <br>
2f3242e8b7a7a521175914084f9404854fc540b4, d9cc3b29fc41c35986aff279b90d51438ce1e516, b668ae333bf1144ad28ea75574d5c7a6f9ae6e90, 77e05dcbf1f5d0e19fe904cdbac9a846faf4260d, 34dbbd8d939ae1f7678d1bdb77850574551fd337 

**Session git history:** 
- Add volume control for up, down, value - *Implemented comprehensive volume control system*
- Add skip, repeat and shuffle to spotify - *Added advanced Spotify playback controls*
- Small syntax errors fixed - *Corrected minor syntax issues*
- Update spotify shuffle - *Improved shuffle functionality*
- mall update to shuffle error handling - *Enhanced error handling for shuffle feature*
---
<br>

## Session 18 
### Sunday July 28th
<br>

**Summary:** This session added repeat and skip functionality to Spotify, implemented remote working capabilities, and fixed various issues with wake word Spotify integration. 

**Git Branch:** main <br>
**Git commits:** <br>
da4d82e3e32f4c6393ee3fc89c81c60a94a54aed, 3ff034faf3af156985dda67953714bb7507905ab, 5759584334b33f38c22eec064d5fbc594d1a3b31, 642f44d60a0b7fa8c9261e908647519732475026 

**Session git history:** 
- Add repeat and skip to spotify, add remote working - *Implemented Spotify controls and remote functionality*
- Fix performance metrics and remote code - *Optimized performance and remote operation code*
- Fix small errors - *Corrected minor bugs*
- Fix wake word spotify stop - *Resolved issue with Spotify stopping on wake word detection*
---
<br>

## Session 17 
### Saturday July 27th
<br>

**Summary:** This session focused on implementing mic lights functionality, removing looping sounds, updating audio files, and cleaning up codebase. 

**Git Branch:** main <br>
**Git commits:** <br>
68b192263df293c3d6444f593bf1c6a5867b4742, 9d244c90b3c26a7ce57baecf3838477251a327a9, fadc2484a3ec56b3e3d568b3d007c342776fb44f, 05a812906999ff3010e3f0b74d020d16f47f046b, 327ca110f4bafdc84c22d02199825746b06dc12d, bf8a19154e1eeb7a7c3bc4b94dccfd786c246c14, 9939a10509e143689ebbb7b97ed28cc16a5e6339, b4242abc1aeaa4a5c845e8fd6369239a21666e26, b398928c0d33db5a516229a9ad17344b7a10f71e, e6a299f391dd45ec6b87b2cf049b6a3ffd259cfb, 24c8a40909b89dafb1be9b4043b98f8dab16d280, 02105ab7d349f62df293e355339a3a8e9591e642, 5574b7898da3e7ea18b44a4d51491462f3537cc6, 73db72f7307a7cd9eadf14fa060eb0683561d4e5, da7147bd8a3b16bb8783430619e37017193c9c5b, 07942c689f6ba9a4358fc78c9cc5952bb1a640e3, 90746ab470c592d907b2ad62bd97dd894c321e6f 

**Session git history:** 
- Remove debugging from detect spotify - *Cleaned up debugging code from Spotify detection*
- Add mic lights scheme - *Implemented LED lighting scheme for microphone*
- Update action processing in main - *Improved main action processing logic*
- Update handling action in main - *Enhanced action handling in main module*
- Update ai prompt, mic lights - *Updated AI prompts and mic light functionality*
- Reorder mic lights - *Reorganized mic light code structure*
- Reorder mic lights - *Further reorganization of mic lights*
- Update lights_processing - *Improved light processing logic*
- Add stopp_pulsing to mic lights - *Added pulsing stop functionality to lights*
- Remove spotify thread - *Removed Spotify threading functionality*
- Remove testing files, completely remove spotify thread imports - *Cleaned up test files and Spotify thread imports*
- Update greeting and generating audio - *Updated audio files for greeting and generation*
- Remove looping sound - *Removed looping audio functionality*
- Change mic lights order - *Reordered mic light operations*
- Cleanup looping sound removal - *Cleaned up code after removing looping sounds*
- Update greeting sound - *Updated greeting audio file*
- Update cleanup output - *Improved cleanup process output*
- Add mpg123 cleanup check - *Added cleanup verification for mpg123*
---
<br>

## Session 16 
### Thursday July 25th
<br>

**Summary:** This session implemented Spotify add to queue functionality, simplified Spotify handling code, and added comprehensive debugging for Spotify type detection. 

**Git Branch:** main <br>
**Git commits:** <br>
499b5e28ea5601ee4bc5d6cdbe2206c7cd92aba3, 8857dd54e6008871aa7dd5ca8d110952aab82a8a, 2cb8cb46ee1eecea91b2527f8e9c36eb8a0160a1, 634516c0c9056e2a4ff3e0447a679065ecf0b13d, 6a8f5cc8cbc8ce5b9bbf72cac57a72b9566280d2, 81e9cc78b530407fa3e883fb8184183c16c90f6a, db90ea3476741088b24ee03074bf306898e74ffb, 3c56399bdf97f1fa467add4b8ce3213e82da451e, 2a35de17cce017b4e84164a8aeff7cebb7cd8705, 4bcd74d42fedee82b00701cc1946c7e3306e3389, 1f1956e515b01da9be6450fafdfd68e62857365d, a98807aa245b315b65a49e2521db66e250e1650d, c5f1b15d3e3ae23cbaa6b622b60ff2f385d8522a, 336a6536bdc9ca9250a1f9205ad604fc890f2ff0, 766d3fbc05cb38a6b9435e66c40476a7fcf2d7d7 

**Session git history:** 
- Add Spotify add to queue - *Implemented Spotify queue addition functionality*
- Fix typo in handle_spotify - *Corrected typo in Spotify handler*
- debug add to queue - *Added debugging for queue functionality*
- Fix syntax error - *Corrected syntax error*
- Add lag time to spotify play - *Added delay before Spotify playback*
- Update typo - *Fixed typo*
- Remove re-add to queue - *Removed redundant queue addition*
- Remove thread add track play logic - *Simplified track addition logic*
- Simplify handle spotify code - *Streamlined Spotify handling code*
- Update handle_spotify and add remote test py - *Enhanced Spotify handler and added remote testing*
- Update to remote test - *Improved remote testing functionality*
- Update spotify detect type - *Enhanced Spotify type detection*
- Debug user_content_type - *Added debugging for content type detection*
- add more spotify type debugging - *Enhanced Spotify type debugging*
- Remove debugging from detect spotify - *Cleaned up debugging code*
---
<br>

## Session 15 
### Wednesday July 24th
<br>

**Summary:** This session focused on AI prompt improvements and mic lights implementation, including cleanup functionality and response handling updates. 

**Git Branch:** main <br>
**Git commits:** <br>
1c7cdca9215f527f5f8ed31104ff1fb877595fc5, 7781f1c60bc4ba9c7629d55119182ad88c2b72ec, 8355a7c9e918002c42437379fbdf79a568d15521, 395aa6537fa2959fed2ce4bd80f6df4d3687a9f2, 17fdc0231d34c2b0e9b83109a4abf34d8d203da7 

**Session git history:** 
- Update ai prompt, Add mic lights class - *Enhanced AI prompts and implemented mic lights*
- Update Mic Lights cleanup - *Improved mic lights cleanup process*
- Update ai prompt - *Refined AI prompt content*
- Update ai Prompt - *Further AI prompt improvements*
- Update for new ai prompt response - *Updated response handling for new AI prompts*
---
<br>

## Session 14 
### Sunday July 21st
<br>

**Summary:** This session involved improving Spotify search functionality, updating AI prompts for better responses, and enhancing cleanup processes. 

**Git Branch:** main <br>
**Git commits:** <br>
0e50afe7b9757de97b51cd92045742772bc50ad7, f74976fba4aa07f19fabc25550f64fa42bf98a3c, 2d334c38194939f9d5666760116215d739ec5cdd, 8649cdbe4daf7002f129ba857ec35ed3ea051d07, 2f26b26b4532fdc8371a41b50203e85646562db1 

**Session git history:** 
- Add improvements to Spotify search - *Enhanced Spotify search capabilities*
- Update ai prompt - *Improved AI prompt content*
- Update ai prompt and success in main - *Updated prompts and success handling*
- Update ai prompt - *Further AI prompt refinements*
- Update cleanup and ai prompt - *Enhanced cleanup and AI prompts*
---
<br>

## Session 13 
### Saturday July 20th
<br>

**Summary:** This session was dedicated to extensive Spotify thread management, including queue functionality, user scopes, and web app authentication improvements. 

**Git Branch:** main <br>
**Git commits:** <br>
11b0452ffc82bd7451d407b966522595bf395dc3, abcc4485fb5daab00f413d857318cfd1589486a0, a7e59fa1c80e4c0dbb978b52bba519295c73494b, 77cca3ad4afc35eaa958a7432cd6ea986b57c6b4, 3313749878e7169ae4c50bf770507d31a1fa25e5, cf924c09499be63c2efb5630d3df4212f4303322, 5ee7b2fff1b31d6734b24c7b55ac5120b89045eb, 582e5ef21fd3af176ba7380d4e0a83827f2972ec, dfbfff5ff8542d9da73b453d756333c98d22ed78, 1cb55db233d12c0db00e389688c24db2eb646fac, 68b24ce248d713916945ae23b287534fe7fae616, 07bfe29da409efc4d29f97af0be74f598b929d70, 68f258f98aa224e601845e1e752e283b0ec7baf9, bc56067000e1e0db96f2bc007e0259513a04d69b, da5b4d61994b2ea4d85fae806d831db558d0e7a6, 1c0743fed4fe7dbd986f93226d0da0dd61d446a3 

**Session git history:** 
- Commit before merging to main - *Prepared for main branch merge*
- Add Spotify thread to constantly add songs to queue - *Implemented continuous queue management*
- Add fall backs to sportify threads - *Added fallback mechanisms for Spotify threads*
- Update possible syntax error in spotify thread - *Fixed potential syntax issues*
- Update spotify thread - *Enhanced Spotify thread functionality*
- Add error handling to spotify thread - *Improved error handling in threads*
- Update spotify thread - *Further thread improvements*
- Update spotify user scopes - *Updated Spotify API user permissions*
- Update web app spotify auth - *Enhanced web app Spotify authentication*
- Update spotify thread to use artist - *Modified thread to handle artist requests*
- Update spotify thread to add only new tracks - *Optimized to add only new tracks*
- add stop to spotify thread immediately - *Implemented immediate thread stopping*
- Update spotify thread stop - *Improved thread stopping mechanism*
- Update spotfiy thread - *Enhanced Spotify thread functionality*
- Update detect spotify type to find exact match - *Improved type detection accuracy*
- Correct syntax error - *Fixed syntax error*
---
<br>

## Session 12 
### Friday July 19th
<br>

**Summary:** This session focused on wake word detection improvements, microphone device management, and Spotify playback enhancements including radio functionality. 

**Git Branch:** main <br>
**Git commits:** <br>
90c46a787c7099119f81873dd0a12c0e0c2e81bb, bbb8baff634e8758d43ee786c93306926690f64a, 2d51028ddfb3902cfc5f4e716ff7d7b720a59759, e1f5bb1cbda77d512b001958c4fb05a05a1c5313, 2ff14dde665e35c4a57c3c550b35fac526b262c9, 0fa782cbc317a3f77919ea15ee93e02e3174497c, b4cbdaf7658cab8ba403c6435fae92c8cb68f797, 0cce508e816e90f52db767686084d50225dcc096, 2e77bee11b92ca5ec8b198ed4dfa3c653c070706, a01256df9e120ba14d5d42849f20a9c3648c7b8c, d888c087999232969c970f11114286154a23cb59, c19bacc645d683445f952ac0544c4773ca9171c4, 008723892ba95b8c21ad8d7691873b886643db9b, 0d5e2965d36c0c95d04359023b0428b9107a0019, 417d68343480cd774c9e2c5c728463255d2923a2, c8f4396e5b30393a0df82ca07fe15a6f8332f8c7, 28ff311f79837f1bbf23f5e3315f7326cccb5c2d, c26a531c4d9f70a7041a5e30a8d85f0dea150056 

**Session git history:** 
- Improve wake word device detection and sensitivity - *Enhanced wake word detection accuracy*
- Add mic device finder - *Implemented microphone device detection utility*
- Add app run script - *Created application startup script*
- Correct typo in run app script - *Fixed typo in startup script*
- Update mongodb confirmation - *Enhanced MongoDB connection confirmation*
- Remove wait_for_device_release to fix seg error - *Fixed segmentation fault by removing device wait*
- Update wake word - *Improved wake word functionality*
- Add missing break to wake word - *Added missing break statement*
- Add debugging to wake word stream - *Enhanced debugging for wake word processing*
- Set input device as none - *Configured input device settings*
- Remove input device input index - *Cleaned up device index handling*
- Update sportify play to add trach uris in a list - *Fixed track URI handling*
- Update handle Spotify to play radio - *Implemented radio playback functionality*
- Add unsaved files from last commit - *Recovered unsaved changes*
- Small update to spotify - *Minor Spotify improvements*
- Add debug to detect type and uri in spotify - *Enhanced Spotify type detection*
- Add debug to logger - *Improved logging debugging*
- Change logger to info - *Set logging level to info*
---
<br>

## Session 11 
### Thursday July 18th
<br>

**Summary:** This session involved extensive audio system improvements including channel configuration, device management, Spotify integration, and action handler implementation. 

**Git Branch:** action_handler <br>
**Git commits:** <br>
015fd860517cc5f50cc4205a3a143bfa2fabd03f, 51ebf620a89b3d69113215d1dfd7933757112c3c, 61307d79f69b3512ddda053f2c124072617db5ea, ba50f3158d647e753fb9bc730c1f20e2ff569075, b67b893224704d558770878e83ce152f9c29848a, b666a4cb9a5f232b87a88b9e9f640ac029188d75, 4651d3912e75d2aefacc33215f1dbe767831f265, b03eab42f84a216923bd929ee756f1d4d120cef6, dbc698c1d62492eb9ef08e76f3dc5b95984d0a75, d98cb2f22c09c045aa8fbf128ecff3b8dbd0ae02, a8acfdd117e84b70f8ac57f5e0ee0173c3b98c6b, 6c61b246c4eff14b9b59cfd67ecaff1b864cf3ea, 7cd6dfb7b99bfd75bed42c3a36300e7b3d2a3ae0, 8925e5cffee88154cde6f0dd9ed8b0168eb68d10, 7cbf3f71f29f1593e0e17cb3ce13d39285503d32, 399c3a64530862398b950946cfbc4090a84146f8, 91406b0154b31025ce52722fffd400ff2776326, 1c6f01213e73eabcb5b639dbe7952ab87d0b81b4, 32abffa9bbda809777b0ea2e4ce85d66593a3ea6, e5ecf5a6b312c8a9ce340094a04fdac6ba8ede65, ba28418c613998e2c64073be4d2a9cc232421c3e, 811872c4018a7a65a6b26f2491d1fe9024403a0f, 658e69ededcc8beb8f1c3a55a7912a702d33c40b 

**Session git history:** 
- Change file structure to include action handler - *Restructured code to include action handlers*
- Add action handler - *Implemented action handling system*
- Update state util to include Spotify playing - *Enhanced state management for Spotify*
- Update logger to give more verbose output - *Increased logging verbosity*
- Update to use handler for Spotify play - *Integrated Spotify with action handlers*
- Update channel to 2 - *Configured audio for 2 channels*
- Update device index for new mic - *Updated microphone device configuration*
- Convert wake word to use 1 channel - *Modified wake word for mono input*
- Update channels to 1 - *Set system to mono audio*
- Update to compensate for system wide 1 channel setting - *Adjusted for mono configuration*
- Update back to 2 channels with wake word conversion - *Reverted to stereo with conversion*
- Merge branch 'main' into action_handler to incorporate new mic and speaker setup - *Merged main branch changes*
- Merged with main for testing - *Prepared for testing*
- Update dispatcher logic - *Improved action dispatching*
- Add debugging for spotify resume - *Enhanced Spotify resume debugging*
- Update get_state - *Improved state retrieval*
- Correct state function calls adding () - *Fixed function call syntax*
- Add function to wait for free device - *Implemented device waiting mechanism*
- Add more aggressive release device - *Enhanced device release process*
- Update to pulseaudio - *Switched to PulseAudio system*
- Update device index to 2 - *Updated device configuration*
- Update ai prompt - *Enhanced AI prompts*
- Change uri to uris - *Fixed URI parameter naming*
---
<br>

## Session 10 
### Saturday July 13th
<br>

**Summary:** This session focused on Spotify service improvements including parameter controls, better logging, MongoDB handling, and wake word integration. 

**Git Branch:** spotify_app <br>
**Git commits:** <br>
22c62a830bb780704003714f51109a182e30282e, bed2dbd9abd8add056360b2ca349d856924cd76c, 48e3bfc33af9d631975f5cbc2ba093a3499c9630, 4c1a73765e5f65a4dcb96353709fe34d51a4853f, 66be7463af2312bdd54f1f952410c69fbddc40b9, a4f5cd3ce58e7a78aae1f819b6a31e85019348af, 9b3274b386ccc2912cf9fc9f41b48489fcbed651, f73b24fbb9a060febe82fff949828187e850e499, 9d37264b95d9924616e3721fdfba446abaf18f16 

**Session git history:** 
- Tidy up imports - *Cleaned up import statements*
- Add Spotify param control and stop command - *Implemented Spotify parameter controls*
- Add better logging and correct mongodb handling in Spotify service - *Enhanced logging and MongoDB integration*
- Update voxSpotify data class - *Improved Spotify data structures*
- Update voxSpotify model - *Enhanced Spotify data models*
- Add stop_playback before wakeword detection - *Implemented Spotify pause on wake word*
- Add Spotify stop when wake word detected - *Enhanced wake word integration*
- Add more cleanup actions - *Improved cleanup processes*
- Fix AudioPlayer circular imports - *Resolved circular import issues*
---
<br>

## Session 9 
### Sunday July 14th
<br>

**Summary:** This session involved AI prompt updates for better explicitness and simplification, along with wake word improvements for Spotify integration. 

**Git Branch:** spotify_app <br>
**Git commits:** <br>
e2d2a7b22530568b00d910f0bc846853752c4c10, 6da4b838bd93311f6874483f50f7700de374d728, 1325195310508559e4bc87ed8b9cbf6559cc96d9, 5fd11a115af6c4567ce27086f43253571907b286 

**Session git history:** 
- Update ai prompt to be more explicit - *Made AI prompts more specific*
- Update ai prompt and simplified it - *Simplified AI prompt structure*
- Update wake word pause spotify - *Enhanced Spotify pause on wake word*
- Add appp state to wake word - *Integrated app state with wake word*
---
<br>

## Session 8 
### Wednesday July 12th
<br>

**Summary:** This session merged audio changes and restructured the Spotify application for better organization and functionality. 

**Git Branch:** main <br>
**Git commits:** <br>
5b298a07154b76a761b845b43e1f57fd4766c08f, 8eb921f0bf2c67367eacabb60ed76bc57ce0022b, ca13cd42f1b5f32da4a45e27890ce25e16ce9f69 

**Session git history:** 
- Merged all audio changes from audio_change2 - *Integrated audio system improvements*
- Change spotify_app structure - *Restructured Spotify application*
- Update settings to remove Spotify content - *Cleaned up settings interface*
---
<br>

## Session 7 
### Tuesday July 9th
<br>

**Summary:** This session involved removing PulseAudio dependencies and cleaning up audio configuration. 

**Git Branch:** main <br>
**Git commits:** <br>
dd88eecda5f6beb43bf853bc81ddc6804f2d8877 

**Session git history:** 
- Remove pulse - *Removed PulseAudio dependencies*
---
<br>

## Session 6 
### Sunday July 7th
<br>

**Summary:** This session added playback routes to the web application for enhanced media control functionality. 

**Git Branch:** main <br>
**Git commits:** <br>
0deb70e7909829815d87c80cd95f764d1cbc4c61 

**Session git history:** 
- Add playback route to web app - *Implemented web app playback controls*
---
<br>

## Session 5 
### Saturday July 6th
<br>

**Summary:** This session focused on Spotify login integration to the web application and debugging improvements. 

**Git Branch:** main <br>
**Git commits:** <br>
d5a06c92a6b3382f16c104e4077541f9c02d9f6f, 622984676c544ef02578b5e1211785240c7da3e2 

**Session git history:** 
- Add Spotify login to web app - *Implemented Spotify web authentication*
- Fix small errors, Add debugging - *Corrected minor issues and added debugging*
---
<br>

## Session 4 
### Tuesday July 2nd
<br>

**Summary:** This session added Spotify playback functionality to voxMate application with debugging and error fixes. 

**Git Branch:** main <br>
**Git commits:** <br>
ef1207175a773d9734489ef6ab63f11dee239d9e, 56ed347402f5e17f20bfae50d52c21a8462f8e87 

**Session git history:** 
- Add Spotify playback to voxMate app - *Implemented Spotify integration*
- Add debugging, change small errors - *Enhanced debugging and fixed errors*
---
<br>

## Session 3 
### Saturday June 30th
<br>

**Summary:** This session involved major file structure reorganization, path updates, and git repository improvements. 

**Git Branch:** voxMate.py_restructure <br>
**Git commits:** <br>
9ea3c17f93eb03e7b3046e7fe4af10fa00623168, 47ab94fbe45ed8ee75eca2c574b53a5e2b70d308, 62462f5a7dad8526bfb2c1a43a67a17ea0cc884b, 04a736213170ef007a2f4e7b491225460240eec2, 4894a2dc2a3a00dbaba528ac10b4c3591818051e, 2a2b134762e7305f84ef1a4ff6e43d6ca5848c73, 69536823f64b58010e49b1d628701692d1171c7e, 725268a700c7d96efd6bbdab684cd111fe373790, 8ce35d10c8998f0556cc581af96a09b78c7ca214 

**Session git history:** 
- Move alsa suppress to separate service - *Separated ALSA suppression into service*
- Change load_env() location to start of main.py - *Moved environment loading*
- Change load_env call to relative path - *Updated path handling*
- Change keyword path - *Updated keyword file paths*
- Change keyword path - *Further path updates*
- Change file structure and removed testing files - *Restructured project and cleaned tests*
- Change local file calls for updated file structure - *Updated file references*
- Change Path local file calls - *Updated path references*
- Update git - *Git repository improvements*
---
<br>

## Session 2 
### Saturday June 29th
<br>

**Summary:** This session focused on modularizing voxMate.py structure, adding Spotify web functionality, and debugging segmentation crashes. 

**Git Branch:** spotify_web <br>
**Git commits:** <br>
6eb98778f4432e6347634a932ac69ff409f3fbbb, b83d2c136f5458652a94ff83453c3d9ab21a4726, 2a792887f60469ab464634750c76c92b716ba1a9, bf54ade09ef08f223d185bd5be4daeed9c3f487e, df88d9f89563442a36b38c751d45a96be86f7d0a, 974417a131b56c3d853399bc47105b3e85aa9ed2 

**Session git history:** 
- Add Spotify login and logout to web app - *Implemented Spotify web authentication*
- Add code refinements to spotify web app - *Enhanced Spotify web interface*
- Change voxMate.py to modularised structure - *Modularized main application*
- Update start and stop scripts - *Improved startup/shutdown scripts*
- Debug python env script call - *Fixed environment script issues*
- Add debugging for seg crash - *Investigated segmentation faults*
---
<br>

## Session 1 
### Friday May 14th - Sunday May 19th
<br>

**Summary:** This initial development session created the core voxMate functionality including recording, speech-to-text, AI integration, text-to-speech, wake word detection, and basic application structure. 

**Git Branch:** main <br>
**Git commits:** <br>
2f02b651632c6c16caf8765ed5f6c6544a97ec5e, 79e2d2bf27f76084b46b1e3b0d9a7b1a2d2417de, 88db215b042ff9dc08f9340246f5f809e1ff4810, 6428c09f43b5b79d1515ebad27721a905d6a235f, 62b52ce14ee85cff91c2cbf531ef5c4d22aa835b, 33897e0911c005254dc97596b36cc526c87c3ebe, a3d0c164e252cb170cf8b182481a31f00dea7d34, fe2d9efb4d2702357b748d9d230755858af9acec, d3539d51fe2ac9ff6274eb25187fa0fbad14706c, 7b2213087c383f5b8198604943f6876b4b31d2d0, def353e2face1a715786c7df2e60445a8737d9f1, 667585091ada9821123753e091844b70866ba6f1, c8003b2a6a02e2a0fce9940e5c6ceb3975296162, 3b9f092a21310333f0c145617e429b26559ba3e3, 35cae67b818af80af9f4f266d6936741b6d5cb04, 0edeb7a1380a339ab3b734c6c81b1dd3411b1da7, a07e5a8f0b007a483fc9e394996b7f6cf61ed5b0 

**Session git history:** 
- Recording script developed - *Created audio recording functionality*
- STT Developed - *Implemented speech-to-text conversion*
- AI API script developed - *Integrated AI API for responses*
- pyttsx TTS script developed - *Implemented text-to-speech with pyttsx*
- piper TTS script developed - *Added Piper TTS support*
- gtts TTS script developed - *Implemented Google TTS integration*
- Wake word script developed - *Created wake word detection*
- Question end detection script developed - *Implemented question detection*
- Complete voxMate Test developed - *Created comprehensive test suite*
- voxMate with groq developed - *Integrated Groq AI service*
- voxMate script small adjustments - *Fine-tuned main script*
- Generating audio added - *Added audio generation feedback*
- Add looping audio (generating) - *Implemented looping generation audio*
- Remove vosk add whisper - *Switched from Vosk to Whisper*
- Add wake word feature and greeting audio - *Enhanced wake word with audio feedback*
- Add question end detection - *Implemented question completion detection*
---
<br>