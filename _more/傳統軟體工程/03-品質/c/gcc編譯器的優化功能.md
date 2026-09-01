# gcc 編譯器的優化功能

gcc 參數 -- https://blog.csdn.net/qq_31108501/article/details/51842166

* -O0 不優化 (預設)
* -O1 部分優化
* -O2 更多優化
* -O3 最高優化

## 關鍵字

1. volatile : 告訴編譯器該變數為揮發性，避免編譯器過度優化
2. register : 請將變數儲存在暫存器

## 文章
* [你所不知道的 C 語言：編譯器和最佳化原理篇](https://hackmd.io/@sysprog/c-prog/%2Fs%2FHy72937Me)
* https://www.cs.cmu.edu/~15745/handouts.html
* http://hackga.com/search/tag/compiler

參考

* https://en.wikipedia.org/wiki/Optimizing_compiler
* https://en.wikipedia.org/wiki/Loop_optimization
* https://en.wikipedia.org/wiki/Basic_block
* https://en.wikipedia.org/wiki/Static_single_assignment_form
* https://en.wikipedia.org/wiki/Control-flow_graph
* https://en.wikipedia.org/wiki/Interprocedural_optimization
* https://en.wikipedia.org/wiki/Object_code_optimizer
* https://en.wikipedia.org/wiki/Side_effect_(computer_science)
* https://en.wikipedia.org/wiki/Instruction_pipelining
* https://en.wikipedia.org/wiki/Inline_expansion

重要技巧 -- https://en.wikipedia.org/wiki/Optimizing_compiler

* https://en.wikipedia.org/wiki/Register_allocation
* https://en.wikipedia.org/wiki/Peephole_optimization
    * a multiplication of a value by 2 might be more efficiently executed by left-shifting the value or by adding the value to itself
    * Peephole optimization involves changing the small set of instructions to an equivalent set that has better performance. 
* Local optimizations
    * https://en.wikipedia.org/wiki/Basic_block
    * https://www.tutorialspoint.com/compiler_design/compiler_design_code_optimization.htm
    * https://www2.cs.arizona.edu/~collberg/Teaching/453/2009/Handouts/Handout-15.pdf

範例 -- Loop_optimization : https://en.wikipedia.org/wiki/Loop_optimization

* https://en.wikipedia.org/wiki/Loop_fission_and_fusion
* https://en.wikipedia.org/wiki/Induction_variable
* https://en.wikipedia.org/wiki/Loop_inversion
* https://en.wikipedia.org/wiki/Loop_interchange
* https://en.wikipedia.org/wiki/Loop-invariant_code_motion
* https://en.wikipedia.org/wiki/Loop_nest_optimization
* https://en.wikipedia.org/wiki/Loop_splitting
* https://en.wikipedia.org/wiki/Loop_unswitching
* https://en.wikipedia.org/wiki/Software_pipelining
* https://en.wikipedia.org/wiki/Automatic_parallelization

範例 -- Data-flow optimizations
* https://en.wikipedia.org/wiki/Common_subexpression_elimination
* https://en.wikipedia.org/wiki/Constant_folding
* https://en.wikipedia.org/wiki/Induction_variable

範例 -- Code generator optimizations
* https://en.wikipedia.org/wiki/Register_allocation
* https://en.wikipedia.org/wiki/Instruction_selection
* https://en.wikipedia.org/wiki/Instruction_scheduling
    * Avoid pipeline stalls by rearranging the order of instructions.
    * Avoid illegal or semantically ambiguous operations
* https://en.wikipedia.org/wiki/Branch_predictor
