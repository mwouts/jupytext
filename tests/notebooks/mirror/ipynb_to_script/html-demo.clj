;; ---
;; jupyter:
;;   kernelspec:
;;     display_name: Clojure
;;     language: clojure
;;     name: clojure
;; ---

;; # Clojupyter Demo
;;
;; This example notebook is from the [Clojupyter](https://github.com/clojupyter/clojupyter/blob/1637f6b2557f01db1e35bae5389bc38522eefe9a/examples/html-demo.ipynb) project.
;; This notebook demonstrates some of the more advanced features of Clojupyter.

;; ## Displaying HTML
;;
;; To display HTML, you'll need to require a clojupyter helper function to change the cell output

(require '[clojupyter.misc.display :as display])

(println ">> should print some text")
;; displaying html
(display/hiccup-html 
    [:ul 
     [:li "a " [:i "emphatic"] " idea"]
     [:li "a " [:b "bold"] " idea"]
     [:li "an " [:span {:style "text-decoration: underline;"} "important"] " idea"]])

;; We can also use this to render SVG:

(display/hiccup-html
    [:svg {:height 100 :width 100 :xmlns "http://www.w3.org/2000/svg"}
            [:circle {:cx 50 :cy 40 :r 40 :fill "red"}]])

;; ## Adding External Clojure Dependencies 
;;
;; You can fetch external Clojure dependencies using the `clojupyter.misc.helper` namespace. 

(require '[clojupyter.misc.helper :as helper])

(helper/add-dependencies '[org.clojure/data.json "0.2.6"])
(require '[clojure.data.json :as json])

(json/write-str {:a 1 :b [2, 3] :c "c"})

;; ## Adding External Javascript Dependency
;;
;; Since you can render arbitrary HTML using `display/hiccup-html`, it's pretty easy to use external Javascript libraries to do things like generate charts. Here's an example using [Highcharts](https://www.highcharts.com/).
;;
;; First, we use a cell to add javascript to the running notebook:

(helper/add-javascript "https://code.highcharts.com/highcharts.js")

;; Now we define a function which takes Clojure data and returns hiccup HTML to display:

(defn plot-highchart [highchart-json]
  (let [id (str (java.util.UUID/randomUUID))
        code (format "Highcharts.chart('%s', %s );" id, (json/write-str highchart-json))]
      (display/hiccup-html 
        [:div [:div {:id id :style {:background-color "red"}}]
                   [:script code]])))

;; Now we can make generate interactive plots (try hovering over plot):

;; +
(def raw-data (map #(+ (* 22 (+ % (Math/random)) 78)) (range)))
(def data-1 (take 500 raw-data))
(def data-2 (take 500 (drop 500 raw-data)))

(plot-highchart {:chart {:type "line"}
                 :title {:text "Plot of random data"}
                 :series [{:data data-1} {:data data-2}]})
;; -


