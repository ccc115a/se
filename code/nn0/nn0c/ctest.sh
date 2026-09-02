set -x

gcc gpt0.c nn0.c gpt0main.c -o gpt0main
./gpt0main ../_data/corpus/tw.txt

# python test_nn0.py
