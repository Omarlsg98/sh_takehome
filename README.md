# Serif Health Takehome: Omar Sanchez

This is the solution for the Serif Health Takehome by Omar Sanchez

Run with ```python src/main.py configs/config.yaml```

## Objective 

Write some code that can open an index file, stream through it, and isolate a set of network files in the index. Asnwer:
what is the list of machine readable file URLs that represent the Anthem PPO network in New York state?

## My solution

I used gzip and ijson to read the compressed json file iteratively. The program traverses the index file checking one reporting_structure item at a time. From here, the program filters out the files that don't have the path "/anthem/NY" (files realted to NY that had information related to the plan_type), and outputs a list of the reamining files with a corresponding EIN code. This EIN code is used to get the "display name" of the file which can be found under the URL "https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/{ein_code}.json". The display name has the information about the plan type (PPO/EPO/HMO), so this name is used to filter out the non PPO files.

## Time to write
It took me 2 hours to understand the data/problem and 1 hour to code.

## Time to run
The code takes 5 mins and 30 secs to run.

## Tradeoffs
- I choose to download on demand the EIN json files to only get the relevant fiels and to allow for new EIN values in the future, even though it adds this download time to the process.
- The URLs are filtered as soon as possible to save memory RAM, this makes the program too specialized for this use case.