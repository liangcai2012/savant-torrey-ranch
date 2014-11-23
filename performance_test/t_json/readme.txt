The purpose of the project: Test the performance of java package [org.json.simple] and [com.google.gson] that converts a map to a JSON 1 million times.  The map has 10 elements: 1 timestamp,  3 doubles, and 6 integers.
Test result: [org.json.simple] is about 30% faster than [com.google.gson] on my windows 7.
[org.json.simple] is about 10% faster than [com.google.gson] on my centos 6 VM.
