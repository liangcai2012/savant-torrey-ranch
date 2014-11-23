[test result] 
OS -- centos 6.6 64-bits  VM 
1. The number of shared memory transfer(between java app and python app) per second is about 1000.The default maxinum shared meory size is 68,719,476,736 bytes!
2. The write speed to shard memroy is about 300M bytes / second.
3.I does not test the read speed. The read speed should be about the same or faster than write speed.
[how to run test] 
development enviroment OS: linux. IDE: Netbeans. You need to create a Eclipse java project, and add the java source files to the project if you use Eclipse IDE.
1. Use netbeans IDE to build java SharedMem project.
2. Run SharedMem/run_speedtest.sh for testing shard memroy write speed.
3. Run [shared memory transfer speed] test
   a. First run SharedMem/run_transferspeed.sh
   b. Then run python test client SharedMem/run_consumer.sh



