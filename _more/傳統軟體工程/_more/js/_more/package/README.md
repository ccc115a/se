# deno 套件

* 標準函式庫 -- https://deno.land/std@0.88.0
* 第三方函式庫 -- https://deno.land/x

## 發布

只要有辦法放上網都能發布，例如放上

1. github pages
2. npm 發佈後，到 https://dev.jspm.io/package_name 去取就行了！

但若要上 deno.land/x 就得到

* https://deno.land/x

拉到最下面，選 Add a Module 填入你的套件！

詳細方法請參考文章

* [How to Add Third Party Library Deno.js ?](https://www.geeksforgeeks.org/how-to-add-third-party-library-deno-js/)

```
Now comes the Publishing part-

Add your module to your Github and enable the actions from your repo.
Make the repo public.
Now go to DATABASE.JSON.
Add your module details in the following format.
"my_library_name": {
    "type": "github",
    "owner": "",
    "repo": ""
}
Now create pull request to update the file.
Write “Add `your_module_name` to Deno.
Make Pull Request.
Now your updated file need to pass some tests and you are good to go.
Successfully created pull request. Wait for the approval.
```
