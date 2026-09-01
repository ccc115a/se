# kubernetes

* https://azure.microsoft.com/zh-tw/topic/what-is-kubernetes/#overview (讚)
    * [使用您的 Azure 免費帳戶部署及管理 Kubernetes](https://azure.microsoft.com/zh-tw/free/kubernetes-service/) (這是一門雲端主機公司的好生意)

新式應用程式漸漸採用容器作為架構，應用程式的相依性和設定就封裝在這個微服務中。Kubernetes (讀音為 “koo-ber-net-ees”) 是開放原始碼軟體，用於大規模部署與管理這些容器，在希臘文中，這也表示船舵手或領航員。使用 Kubernetes (有時稱為 “k8s” 或 “k-eights”) 可以更快地建置、傳遞及調整容器化應用程式。

Kubernetes 的運作方式
隨著應用程式發展到跨多個伺服器部署的多個容器，操作方式也變得更加複雜。為了管理這樣的複雜性，Kubernetes 提供了開放原始碼 API，可用於控制這些容器的執行方式和位置。

Kubernetes 可根據可用的計算資源及每個容器的資源需求，來協調虛擬機器的叢集，並排程容器在這些虛擬機器上執行。容器會分組成 Pod，即 Kubernetes 的基本作業單位，這些 Pod 可調整成您需要的狀態。

Kubernetes 也可自動管理服務探索、納入負載平衡、追蹤資源配置，以及根據計算使用率進行調整。此外還可檢查個別資源的健康狀態，並透過自動重新啟動或複寫容器使應用程式自我修復。

* https://www.redhat.com/zh/topics/containers/what-is-kubernetes

Docker运行状态
Docker（点击查看Docker原理） 技术仍然执行它原本的工作。当 kubernetes 将容器集调度到一个节点上时，该节点上的 kubelet 会发送指令让 docker 启动指定的容器。kubelet 随后会不断从 docker 收集这些容器的状态，并将这些信息汇集至主机。Docker 将容器拉至该节点，并按照常规启动和停止这些容器。不同在于，自动化系统要求 docker 在所有节点上对所有容器执行这些操作，而非要求管理员手动操作。
