

```js
var a = [1,2,3]
var b = [0,0,0]

a = [4,5]
//...



```

```js
var a = new Array(100)

for (var i=0; i<1000000; i++) {
  a = new Array(100) 
}
```

```cpp
int *a;

for (int i=0; i<1000000; i++) {
  a = malloc(i*sizeof(int));
  // ....
  free(a);
}
```

```cpp
int *a;

a = malloc(100*sizeof(int));
for (int i=0; i<1000000; i++) {
  // ....
}
free(a);
```


```cpp
int buf[10000000000];
int *a;

for (int i=0; i<1000000; i++) {
  a = a+i*sizeof(int);
  // ....
}
```