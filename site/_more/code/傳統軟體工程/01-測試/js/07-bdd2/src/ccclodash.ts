// chunk(['a', 'b', 'c', 'd'], 2) => [['a', 'b'], ['c', 'd']]
// chunk(['a', 'b', 'c', 'd'], 3) => [['a', 'b', 'c'], ['d']]
export function chunk(list:any[], n:number):any[] {
  const clist = []
  for (let i=0; i<list.length; i+=n) {
    clist.push(list.slice(i, i+n))
  }
  return clist
}

// _.compact([0, 1, false, 2, '', 3]), [ 1, 2, 3]
export function compact(list:any[]) {
  const clist = []
  for (let o of list) {
    if (o) clist.push(o)
  }
  return clist
}


// var array = [1];
// var other = _.concat(array, 2, [3], [[4]]);
// other equalTo([1, 2, 3, [4]])
export function concat(...args: any[]) {
  var clist:any[] = []
  for (let i=0; i<args.length; i++) {
    clist = clist.concat(args[i])
  }
  return clist
}
