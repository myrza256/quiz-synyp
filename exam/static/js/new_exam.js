function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}


async function post(url, data){
    let dataReceived;
    let response = await fetch(url, {
			method: "POST",
			headers: { "Content-Type": "plain/text" },
			body: data
		});
    dataReceived = await response.json();
    return dataReceived;
}

document.cookie = `token=${localStorage.getItem("user-token")}`

let form = new Vue({
    el: "#vue-container",
    data: {
        firstAdditional: false,
        secondAdditional: false,
        hours: 0,
        minutes: 0,
        seconds: 0,
        secondLessons: {},
        lessons: [],
        obligatorys: {}
    },
    methods: {
        set_first_additional: function (id) {
            document.cookie = "first_additional=" + encodeURIComponent(id);
            this.firstAdditional = id;
        },
        set_second_additional: function (id) {
            document.cookie = "second_additional=" + encodeURIComponent(id);
            this.secondAdditional = id;
        },
        unset_second_additional: function () {
            let first_additional = getCookie("first_additional");
            if (first_additional !== undefined){
                document.cookie = "first_additional=" + encodeURIComponent(first_additional);
            } else{
                document.cookie = "";
            }
            this.secondAdditional = false;

        },
        unset_additionals: function () {
            document.cookie = "";
            this.firstAdditional = false;
            this.secondAdditional = false;
        },
    },
    created: function () {
        post("https://test.insynyp.online/api/", `{"action": "get_subjects"}`)
            .then( res => {
                    this.obligatorys = res.subjects.slice(0, 3);
                    this.lessons = res.subjects.slice(3);
                    this.secondLessons = res.second_lessons;
                }
            );
    }
});
