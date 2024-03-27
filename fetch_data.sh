#!/bin/bash
for i in 1k 2k 4k 6k 8k 12k 16k 32k 64k 128k
do
wget http://opencompass.openxlab.space/utils/AdaLEval/stackselect_$i.json -O data/stackselect_$i.json;
wget http://opencompass.openxlab.space/utils/AdaLEval/textsort_$i.json -O data/textsort_$i.json;
done