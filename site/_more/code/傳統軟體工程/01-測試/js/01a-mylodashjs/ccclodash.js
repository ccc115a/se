// chunk(['a', 'b', 'c', 'd'], 2) => [['a', 'b'], ['c', 'd']]
// chunk(['a', 'b', 'c', 'd'], 3) => [['a', 'b', 'c'], ['d']]
export function chunk(list, n) {
  const clist = []
  for (let i=0; i<list.length; i+=n) {
    clist.push(list.slice(i, i+n))
  }
  return clist
}

