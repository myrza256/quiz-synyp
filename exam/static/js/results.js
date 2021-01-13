let exam_data = JSON.parse(document.getElementById('djangoData').textContent);


async function post(url, data){
    let dataReceived;
    let response = await fetch(url, {
			method: "POST",
			headers: { "Content-Type": "plain/text" },
			body: data
		});
    dataReceived = await response;
    return dataReceived.json();
}


let exam = new Vue({
    el: "#vue-container",
    data: {
        menuOpened: false,
        questions: [],
        subjects: [],
        activeSubject: "",
        correctAnswers: [],
        selectedAnswers: [],
        incorrectAnswers: []
    },
    methods: {
        selectSubject: function (id) {
            this.activeSubject = id;
        },
        checkCorrect: function (id) {
            for (let i in this.correctAnswers){
                if (id === this.correctAnswers[i]){
                    return true
                }
            }
            for (let i in this.incorrectAnswers){
                if (id === this.incorrectAnswers[i]){
                    return false
                }
            }
            return "unselected"
        }
    },
    created: function(){
        this.activeSubject = exam_data.subjects[0].id;
        this.subjects = exam_data.subjects;
        for (let subject in this.subjects){
            this.selectedAnswers[this.subjects[subject].id] = false;
        }
        post("http://127.0.0.1:8000/api/",
            `{"action": "get_questions", "exam_id": ${exam_data.examId}}`)
            .then( res => {
                this.questions = res;
                post("http://127.0.0.1:8000/api/",
            `{"action": "get_selected", "exam_id": ${exam_data.examId}}`)
                    .then(
                        res => {
                            console.log(res);
                            for (let i in res){
                                if (res[i].is_correct){
                                    this.correctAnswers.push(res[i].id)
                                }
                                else{
                                    this.incorrectAnswers.push(res[i].id)
                                }
                            }
                        })
                }
            );
        }});