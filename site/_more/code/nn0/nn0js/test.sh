set -x

node examples/auto_grad.js
node examples/linear_classify.js
node examples/xor.js
# node examples/test_cnn0.js
node examples/test_gpt0.js ../../_data/corpus/chinese.txt
