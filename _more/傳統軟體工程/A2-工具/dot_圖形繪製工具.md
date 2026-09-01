# dot 圖形繪製工具

## graph 圖形 -- graphviz:dot

* https://edotor.net/

圖靈機範例：

```
digraph TuringMachine_anbncn {
	rankdir=LR;
	size="8,5"

	node [shape = doublecircle]; 0 3;
	node [shape = circle];

	0 -> 1 [ label = "a/_,R" ];
	1 -> 1 [ label = "a/a,R" ];
	1 -> 1 [ label = "x/x,R" ];
	1 -> 2 [ label = "b/x,R" ];
	2 -> 2 [ label = "x/x,R" ];
	2 -> 2 [ label = "b/b,R" ];
	2 -> 5 [ label = "c/x,L" ];
	5 -> 5 [ label = "x/x,L" ];
	5 -> 5 [ label = "a/a,L" ];
	5 -> 0 [ label = "_/_,R" ];
	0 -> 4 [ label = "x/x,R" ];
	0 -> 3 [ label = "_/_,L" ];
	4 -> 4 [ label = "x/x,R" ];
	4 -> 3 [ label = "_/_,L" ];
}

```
