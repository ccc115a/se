export function chunk(array=[], n) {
  const clist = []
    for (let i=0; i <= array.length; i+=n) {
      clist.push(  array.slice(i, i + n))
      }
         return clist
         }


