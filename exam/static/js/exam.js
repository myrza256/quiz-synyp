let exam_data = JSON.parse(document.getElementById('djangoData').textContent);
Vue.config.productionTip = false;
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


let endExam = new Vue({
    el: "#end_exam",
    data:{
        rightAnswers: false
    }
});


let exam = new Vue({
    el: "#vue-container",
    data: {
        examData: exam_data,
        menuOpened: false,
        timeLeft: 12600,
        seconds: "00",
        minutes: 30,
        hours: 3,
        questions: [],
        subjects: [],
        activeSubject: "",
        selectedAnswers: {}
    },
    methods: {
        save: function () {
            post("http://127.0.0.1:8000/api/", JSON.stringify({
                "action": "upload_answers",
                "answers": this.selectedAnswers,
                "exam_id": exam_data.examId,
                "user_id": exam_data.userId
            }))
                .then(
                    res=>{
                        window.location.replace(`http://127.0.0.1:8000/results/${exam_data.examId}/`);
                    }
                )
        },
        selectAnswer: function (id) {
            this.selectedAnswers[id] = true;
        },
        unselectAnswer: function (id) {
            this.selectedAnswers[id] = false;
        },
        selectSubject: function (id) {
            this.activeSubject = id;
        }
    },
    created: function(){
        this.activeSubject = exam_data.subjects[0].id;
        this.timeLeft = exam_data.timeLeft;
        this.seconds = this.timeLeft % 60;
        this.minutes = ((this.timeLeft - this.seconds) / 60) % 60;
        this.hours = (this.timeLeft - this.seconds - 60 * this.minutes) / 3600;
        this.subjects = exam_data.subjects;
        for (let subject in this.subjects){
            this.selectedAnswers[this.subjects[subject].id] = false;
        }
        post("http://127.0.0.1:8000/api/",
            `{"action": "get_questions", "exam_id": ${exam_data.examId}}`)
            .then( res => {
                console.log(res);
                this.questions = res;
                }
            );
        setInterval(function(){
	    if (exam.timeLeft !== 0){
            exam.timeLeft -= 1;
            exam.seconds = exam.timeLeft % 60;
            exam.minutes = ((exam.timeLeft - exam.seconds) / 60) % 60;
            exam.hours = (exam.timeLeft - exam.seconds - 60 * exam.minutes) / 3600;
            if (exam.seconds < 10){
                exam.seconds = "0" + exam.seconds;
            }
            if (exam.minutes < 10){
                exam.minutes = "0" + exam.minutes;
            }
	    } else {
	        window.location.replace(`http://127.0.0.1:8000/results/${exam_data.examId}/`);
        }
	}, 1000);
        // this.$nextTick().then(
        //     ()=>{
        //         MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
        //     }
        // )
    }
});