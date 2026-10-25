window.onload = function () {
	function paddy(num, padlen, padchar) {
		var pad_char = typeof padchar !== 'undefined' ? padchar : '0';
		var pad = new Array(1 + padlen).join(pad_char);
		return (pad + num).slice(-pad.length);
	}
	
    const helpers = {
        getTodayDate: function (months, years) {
            if(years == undefined) years = 0;
            var today = new Date();
			var endday = new Date();
			endday.setDate(today.getDate() + 30);
			if(months == 2) return endday.getFullYear() + "-" +  paddy(endday.getMonth()+1,2) + "-" + ('0' + endday.getDate()).slice(-2);
            else return (today.getFullYear() + years) + '-' + ('0' + (today.getMonth() + months)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
        },

        resetSelects: function (id) {
            var childs = id.types.options;
            for(var i = 0; i < childs.length; i++) {
                id.types.options[i].removeAttribute('selected');
            }
            id.types.options[0].setAttribute('selected', true);
        },

        resetAdvert: function (html) {
            UX.boxes.advertBox.innerHTML = '';

            if(html != undefined) {
                UX.boxes.advertBox.insertAdjacentHTML('beforeend', html);
            }

            return false;
        },

        getMonth: function (month) {
            switch(month) {
                case 0: return 'Января';
                case 1: return 'Февраля';
                case 2: return 'Марта';
                case 3: return 'Апреля';
                case 4: return 'Мая';
                case 5: return 'Июня';
                case 6: return 'Июля';
                case 7: return 'Августа';
                case 8: return 'Сентября';
                case 9: return 'Октября';
                case 10: return 'Ноября';
                case 11: return 'Декабря';
            }
        },

        getDay: function (date) {
            var date = new Date(date);

            switch(date.getDay()) {
                case 1: return "Понедельник, " + date.getUTCDate() + " " + helpers.getMonth(date.getMonth()) + " " + date.getUTCFullYear();
                case 2: return "Вторник, " + date.getUTCDate() + " " + helpers.getMonth(date.getMonth()) + " " + date.getUTCFullYear();
                case 3: return "Среда, " + date.getUTCDate() + " " + helpers.getMonth(date.getMonth()) + " " + date.getUTCFullYear();
                case 4: return "Четверг, " + date.getUTCDate() + " " + helpers.getMonth(date.getMonth()) + " " + date.getUTCFullYear();
                case 5: return "Пятница, " + date.getUTCDate() + " " + helpers.getMonth(date.getMonth()) + " " + date.getUTCFullYear();
                case 6: return "Суббота, " + date.getUTCDate() + " " + helpers.getMonth(date.getMonth()) + " " + date.getUTCFullYear();
                case 7: return "Воскресенье, " + date.getUTCDate() + " " + helpers.getMonth(date.getMonth()) + " " + date.getUTCFullYear();
            }
        },

        setWeekType: function () {

            var weekType = 'Текущая неделя является ';

            var year = new Date().getFullYear();
			
			
            var start = new Date(year, 7, 31).getTime();
           /*  var startbaz = new Date(year, 7, 31); */
            var now = new Date().getTime();
			var diff = Math.floor(now - start);
            var week =  Math.floor(diff / (1000 * 60 * 60 * 24 * 7));
			console.log(week);
            week % 2 ? weekType += 'четной' : weekType += 'нечетной';

            document.getElementById('weekType').innerText = weekType;

        },

        formatDepartments: function (data) {

            for (var prop in data) {
                switch (data[prop].name) {
                    case 'Дневное': {
                        data[prop].name = 'Очная';
                        break;
                    }
                    case 'Вечернее': {
                        data[prop].name = 'Очно-заочная';
                        break;
                    }
                    case 'Заочное 3.10': {
                        data[prop].name = 'Заочная 3 года 10 мес';
                        break;
                    }
                    case 'Заочное 5.10': {
                        data[prop].name = 'Заочная 5 лет';
                        break;
                    }
                }
            }

            return data;
        },

        implodeProps: function (data) {
            var result = '';

            for (var prop in data) {
                result += '&' + prop + '=' + data[prop];
            }

            return result;
        },

        getDayOfWeek: function (day) {
            var days = [
                'Понедельник',
                'Вторник',
                'Среда',
                'Четверг',
                'Пятница',
                'Суббота',
                'Воскресенье'
            ];

            return days[day];
        },

        dispatchDefaultAdvert: function (week, type, department) {
			console.log(type);
            if(Object.keys(week).length <= 0) {
                helpers.resetAdvert('<h3 style = "text-align: center; color: #ff0000;">Извините, но расписание по введённым датам не найдено.</h3>');
                return false;
            }

            var html = '';

            if(type == 1 && department == 1) {
                html += "<h2>Основное расписание</h2>";
                for(var day in week) {

                    var table = '';
                    table += "<table class = 'table raspTable'>";
                    table += "<thead>";
                    table += "<tr>";
                    table += "<th colspan='5'>";
                    table += "<h3>"+ helpers.getDayOfWeek(day-1) +"</h3>";
                    table += "</th>";
                    table += "</tr>";
                    table += "<tr>";
                    table += "<th style = 'width: 175px;'>Пара</th>";
                    table += "<th style = 'width: 300px;'>Дисциплина</th>";
                    table += "<th style = 'width: 350px;'>Преподаватель</th>";
                    table += "<th style = 'width: 100px;'>Дист/Ауд</th>";
                    table += "<th style = 'width: 200px;'>Примечание</th>";
                    table += "<th>Неделя</th>";
                    table += "</tr>";
                    table += "</thead>";
                    table += "<tbody>";

                    for(var paraList in week[day]) {

                        if (week[day][paraList].length == 1) {
                            var para = week[day][paraList][0];
							//console.log(para);
                            /*  console.log(`${para.para_title} ${para.potok_list} ${para.distant}`)
                             console.log(para.distant) */
                            const isLectureDistance = (para.potok_list != null && para.distant === null) || para.distant == 1
							
                            var url = false;
                            if(para.url) url = '<a href="' + para.url + '">Дистанционно</a>';
                            else url = 'Дистанционно';

                            table += "<tr>";
                            table += "<td style = 'vertical-align: middle;'>" + para.para_title + " / " + para.para_time + "</td>";
                            table += "<td>" + para.predmet_name + " / " + para.para_type + "</td>";
                            table += "<td>" + para.prepod_surname + " " + para.prepod_name + " " + para.prepod_initials + "</td>";
                            table += "<td style='text-align: center;'>" + ( isLectureDistance ? url : para.aud) + "</td>";
                            table += "<td style='text-align: center;'>" + ( para.comment != null ? para.comment : '') + "</td>";
                            table += "<td>";

                            switch(para.para_weekType) {
                                case '0': {
                                    table += "Всегда";
                                    break;
                                }
                                case '1': {
                                    table += 'Нечетная';
                                    break;
                                }
                                default: {
                                    table += 'Четная';
                                }
                            }

                            table += "</td>";
                            table += "</tr>";
                        } else {
                            for (var i = 0; i < week[day][paraList].length; i++) {

                                var para = week[day][paraList][i];
								const isLectureDistance = (para.potok_list != null && para.distant === null) || para.distant == 1
								var url = false;
								if(para.url) url = '<a href="' + para.url + '">Дистанционно</a>';
								else url = 'Дистанционно';
                                if(i == 0) {

                                    table += "<tr>";
                                    table += "<td rowspan = "+week[day][paraList].length+" style = 'vertical-align: middle;'>" + para.para_title + " / " + para.para_time + "</td>";
                                    table += "<td>" + para.predmet_name + " / " + para.para_type + "</td>";
                                    table += "<td>" + para.prepod_surname + " " + para.prepod_name + " " + para.prepod_initials + "</td>";
									table += "<td style='text-align: center;'>" + ( isLectureDistance ? url : para.aud) + "</td>";
                                    table += "<td style='text-align: center;'>" + ( para.comment != null ? para.comment : '') + "</td>";
                                    table += "<td>";

                                    switch(para.para_weekType) {
                                        case '0': {
                                            table += "Всегда";
                                            break;
                                        }
                                        case '1': {
                                            table += 'Нечетная';
                                            break;
                                        }
                                        default: {
                                            table += 'Четная';
                                        }
                                    }

                                    table += "</td>";
                                    table += "</tr>";

                                } else {

                                    table += "<tr>";
                                    table += "<td>" + para.predmet_name + " / " + para.para_type + "</td>";
                                    table += "<td>" + para.prepod_surname + " " + para.prepod_name + " " + para.prepod_initials + "</td>";
									table += "<td style='text-align: center;'>" + ( isLectureDistance ? url : para.aud) + "</td>";
                                    table += "<td style='text-align: center;'>" + ( para.comment != null ? para.comment : '') + "</td>";
                                    table += "<td>";

                                    switch(para.para_weekType) {
                                        case '0': {
                                            table += "Всегда";
                                            break;
                                        }
                                        case '1': {
                                            table += 'Нечетная';
                                            break;
                                        }
                                        default: {
                                            table += 'Четная';
                                        }
                                    }

                                    table += "</td>";
                                    table += "</tr>";
                                }

                            }
                        }
                    }

                    table += "</tbody>";
                    table += "</table>";

                    html += table;
                }
            } else if (type == 2 || type == 3 && department == 1) {
				if(type == 2) str_type = "экзаменов";
				if(type == 3) str_type = "практик";
                html += "<h2>Расписание "+str_type+"</h2>";
                html += "<table class = 'table raspTable' style = 'width: 100%;'>";
                html += "<thead>";
                html += "<th>Дата и время</th>";
                html += "<th>Дисциплина</th>";
                html += "<th>Тип</th>";
                html += "<th>Преподаватель</th>";
                html += "<th>Дист/Ауд</th>";
                html += "<th>Примечание</th>";
                html += "</thead>";
                html += "<tbody>";

                for (var line in week) {
					if(week[line].url) url = '<a href="' +  week[line].url + '">Дистанционно</a>';
					else url = 'Дистанционно';
                    html += "<tr>";
                    html += "<td>"+ week[line].xdt +"</td>";
                    html += "<td>"+ week[line].predmet_name +"</td>";
                    html += "<td>"+ week[line].para_type +"</td>";
                    html += "<td>" + week[line].prepod_surname + " " + week[line].prepod_name + " " + week[line].prepod_initials +"</td>";
                   // html += "<td>" + (week[line].pgrup == "0" ? '' : week[line].pgrup) +"</td>";
                    html += "<td align='center'>" + ( week[line].distant == "1" ? url : week[line].aud) + "</td>";
                    html += "<td style='text-align: center;'>" + ( week[line].comment != null ? week[line].comment : '') + "</td>";
                    html += "</tr>";
                }

                html += "</tbody>";
                html += "</table>";
            } else {

                // console.log(week);
                for(var day in week) {

                    var table = '';
                    table += "<table class = 'table raspTable'>";
                    table += "<thead>";
                    table += "<tr>";
                    table += "<th colspan='5'>";
                    table += "<h3>" + helpers.getDay(day) + "</h3>";
                    table += "</th>";
                    table += "</tr>";
                    table += "<tr>";
                    table += "<th style = 'width: 175px;'>Пара</th>";
                    table += "<th style = 'width: 300px;'>Дисциплина</th>";
                    table += "<th style = 'width: 350px;'>Преподаватель</th>";
                    table += "<th style = 'width: 200px;'>Дистанционно/Ауд.</th>";
                    table += "<th>Примечание</th>";
                    table += "<th>Неделя</th>";
                    table += "</tr>";
                    table += "</thead>";
                    table += "<tbody>";

                    for (var paraList in week[day]) {

                        if (week[day][paraList].length == 1) {
                            var para = week[day][paraList][0];
							 const isLectureDistance = (para.potok_list != null && para.distant === null) || para.distant == 1
                         // console.log(para);
                            table += "<tr>";
                            table += "<td style = 'vertical-align: middle;'>" + para.para_title + " / " + para.para_time + "</td>";
                            table += "<td>" + para.predmet_name + " / " + para.para_type + "</td>";
                            table += "<td>" + para.prepod_surname + " " + para.prepod_name + " " + para.prepod_initials + "</td>";
                            table += "<td>" + ( para.distant == 1 ?
																		para.url != "" ? 
																							'<a href="' + para.url + '">Дистанционно</a>' : 
																							"<a href='https://sdo.api.nntu.ru/'>Дистанционно</a>" 
																		: para.aud ) + "</td>";
							table += "<td>" + para.comment + "</td>";
                            table += "<td>";

                            switch (para.para_weekType) {
                                case '0': {
                                    table += "Всегда";
                                    break;
                                }
                                case '1': {
                                    table += 'Нечетная';
                                    break;
                                }
                                default: {
                                    table += 'Четная';
                                }
                            }

                            table += "</td>";
                            table += "</tr>";
                        } else {
                            for (var i = 0; i < week[day][paraList].length; i++) {

                                var para = week[day][paraList][i];

                                if (i == 0) {

                                    table += "<tr>";
                                    table += "<td rowspan = "+week[day][paraList].length+" style = 'vertical-align: middle;'>" + para.para_title + " / " + para.para_time + "</td>";
                                    table += "<td>" + para.predmet_name + " / " + para.para_type + "</td>";
                                    table += "<td>" + para.prepod_surname + " " + para.prepod_name + " " + para.prepod_initials + "</td>";
                                    table += "<td>" + ( para.distant == 1 ?  para.url != "" ? '<a href="' + para.url + '">Дистанционно</a>' : "<a href='https://sdo.api.nntu.ru/'>Дистанционно</a>" : para.aud) + "</td>";
                                   table += "<td>" + para.comment + "</td>";
								   table += "<td>";

                                    switch (para.para_weekType) {
                                        case '0': {
                                            table += "Всегда";
                                            break;
                                        }
                                        case '1': {
                                            table += 'Нечетная';
                                            break;
                                        }
                                        default: {
                                            table += 'Четная';
                                        }
                                    }

                                    table += "</td>";
                                    table += "</tr>";

                                } else {

                                    table += "<tr>";
                                    table += "<td>" + para.predmet_name + " / " + para.para_type + "</td>";
                                    table += "<td>" + para.prepod_surname + " " + para.prepod_name + " " + para.prepod_initials + "</td>";
                                    table += "<td>" + ( para.distant == 1 ?  para.url != "" ? '<a href="' + para.url + '">Дистанционно</a>' :  "<a href='https://sdo.api.nntu.ru/'>Дистанционно</a>" : para.aud) + "</td>";
                                    table += "<td>" + para.comment + "</td>";
									table += "<td>";

                                    switch (para.para_weekType) {
                                        case '0': {
                                            table += "Всегда";
                                            break;
                                        }
                                        case '1': {
                                            table += 'Нечетная';
                                            break;
                                        }
                                        default: {
                                            table += 'Четная';
                                        }
                                    }

                                    table += "</td>";
                                    table += "</tr>";
                                }

                            }
                        }
                    }

                    table += "</tbody>";
                    table += "</table>";

                    html += table;
                }
            }

            helpers.resetAdvert(html);
        }
    };

    var HTTP = {
        request: function (type, url, json_decode, data, success, before) {
            var xhr = new XMLHttpRequest(),
                body = '';

            xhr.open(type, url, true);
            xhr.setRequestHeader('Accept', '*/*');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');

            body = helpers.implodeProps(data);

            xhr.send(body);

            if(typeof(before()) !== 'undefined') before();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    success(json_decode ? JSON.parse(xhr.responseText) : xhr.responseText);
                }
            };
        }
    };

    const UX = {
        selects: {
            students: {
                departments: document.getElementById('studentAdvert__controls--department'),
                groups: document.getElementById('studentAdvert__controls--groups'),
                types: document.getElementById('studentAdvert__controls--types')
            }
        },
        inputs: {
            students: {
                dateBefore: document.getElementById('dateBefore'),
                dateAfter: document.getElementById('dateAfter')
            }
        },
        buttons: {
            studentsAdvert: document.getElementById('studentsAdvert'),
            lecturersAdvert: document.getElementById('lecturersAdvert'),
            examBtn: document.getElementById('studentAdvert__controls--examBtn__box')
        },
        boxes: {
            departmentBox: document.getElementById('studentAdvert__controls--department__box'),
            groupsBox: document.getElementById('studentAdvert__controls--groups__box'),
            typesBox: document.getElementById('studentAdvert__controls--types__box'),
            advertBox: document.getElementById('printable'),
            dateBeforeBox: document.getElementById('studentAdvert__controls--dateBefore__box'),
            dateAfterBox: document.getElementById('studentAdvert__controls--dateAfter__box')
        },
        helpers: {
            spinner: function (id) {
                var para = document.createElement("div");
                para.className = 'lds-spinner';
                para.id = id;

                var node = document.createElement("div");
                var headline = document.createElement("h2");
                headline.innerText = "Пожалуйста, подождите...";

                for (var i = 0; i < 12; i++) {
                    para.appendChild(node.cloneNode(true));
                }

                para.appendChild(headline);

                return para;
            },
            insertSpinner: function (box, spinnerId) {
                if(typeof(UX.spinners[spinnerId]) == 'undefined') {
                    box.parentNode.insertBefore(UX.helpers.spinner(spinnerId), box);
                    UX.spinners[spinnerId] = document.getElementById(spinnerId);
                } else {
                    document.getElementById(spinnerId).style.display = 'block';
                }
            },
            hideSpinner: function (box, spinnerId) {
                box.style.display = 'block';
                document.getElementById(spinnerId).style.display = 'none';
            },
            hideBox: function (box) {

            }
        },
        spinners: {}
    };

    const advert = {
        departments: [],
        students: {
            data: {
                departments: [],
                department_id: 1,
                groups: [],
                group_id: null,
                type_id: null,
                dateFrom: null,
                dateTo: null,
                courses: {}
            },
            methods: {
                setDepartmentControls: function () {
                    HTTP.request('GET', '/getdepartments', true, {},
                        function (data) {
                            advert.students.data.departments = data;
                            var departments = helpers.formatDepartments(data);

                            for (let i = 0; i < departments.length; i++) {
                                UX.selects.students.departments.insertAdjacentHTML('beforeend',
                                    "<option value = " + departments[i].id + ">" + departments[i].name + "</option>");
                            }

                            UX.selects.students.departments.insertAdjacentHTML('afterbegin',
                                "<option value = 'null' selected>Выберите форму обучения</option>");

                            UX.helpers.hideSpinner(UX.boxes.departmentBox, "departmentSpinner");
                        },
                        function () {
                            UX.helpers.insertSpinner(UX.boxes.departmentBox, "departmentSpinner");
                        });
                },
                setGroups: function () {
                    HTTP.request('POST', '/getgroups', true, {
                            'department_id': advert.students.data.department_id
                        },
                        function (data) {
                            advert.students.data.groups = data;
                            var proxyGroups = advert.students.data.groups;
                            var groups = [];
                            proxyGroups.filter((group) => {
                                if(group.kurs <= 5) groups.push(group);
                            });

                            UX.selects.students.groups.innerHTML = '';

                            for (let i = 0; i < groups.length; i++) {

                                if(!advert.students.data.courses.hasOwnProperty(groups[i].kurs)) {
                                    advert.students.data.courses[groups[i].kurs] = groups[i].kurs;
                                }

                            }

                            for (var kurs in advert.students.data.courses) {

                                var proxyKurs = kurs+"&nbspКурс";
                                UX.selects.students.groups.insertAdjacentHTML('beforeend',
                                    "<optgroup label = "+proxyKurs+" id = "+kurs+'-kurs'+"></optgroup>");

                            }

                            for (let i = 0; i < groups.length; i++) {

                                if(!advert.students.data.courses.hasOwnProperty(groups[i].kurs)) {
                                    advert.students.data.courses[groups[i].kurs] = groups[i].kurs;
                                }

                                document.getElementById(groups[i].kurs+'-kurs').insertAdjacentHTML('beforeend',
                                    "<option value = " + groups[i].id + ">" + groups[i].name + "</option>");
                            }

                            UX.selects.students.groups.insertAdjacentHTML('afterbegin',
                                "<option value = 'null' selected>Выберите группу</option>");

                            UX.helpers.hideSpinner(UX.boxes.groupsBox, "groupsSpinner");
                        },
                        function () {
                            UX.helpers.insertSpinner(UX.boxes.groupsBox, "groupsSpinner");
                        });
                },
                setAdvert: function () {
                    HTTP.request('POST', '/getschedule', true,
                        {
                            'department_id': advert.students.data.department_id,
                            'group_id': advert.students.data.group_id,
                            'type': advert.students.data.type_id,
                            'date_from': advert.students.data.dateFrom,
                            'date_to': advert.students.data.dateTo
                        },
                        function (data) {
                            helpers.dispatchDefaultAdvert(data, advert.students.data.type_id, advert.students.data.department_id);
							console.log(123);
                            UX.helpers.hideSpinner(UX.boxes.advertBox, "advertSpinner");
                        },
                        function () {
                            helpers.resetAdvert();
                            UX.helpers.insertSpinner(UX.boxes.advertBox, "advertSpinner");
                        })
                }
            }
        }
    };

    init();

    function init() {
        helpers.setWeekType();
        advert.students.methods.setDepartmentControls();
    }

    var app = {
        advert: 'students'
    };

    // Departments select
    UX.selects.students.departments.addEventListener('change', function (e) {
        advert.students.data.department_id = e.target.value;

        helpers.resetAdvert(); // reset advert
        UX.boxes.groupsBox.style.display = 'none'; // hide box with groups
        UX.boxes.typesBox.style.display = 'none'; // hide box with types
        UX.boxes.dateBeforeBox.style.display = 'none';
        UX.boxes.dateAfterBox.style.display = 'none';
        UX.buttons.examBtn.style.display = 'none';
        helpers.resetSelects(UX.selects.students);

        advert.students.data.type_id = 'null'; // rest type
        advert.students.methods.setGroups();
    });

    // Groups select
    UX.selects.students.groups.addEventListener('change', function (e) {
        advert.students.data.group_id = e.target.value;

        if (advert.students.data.group_id == 'null') {
            UX.boxes.typesBox.style.display = 'none';
            return false;
        }

        if(advert.students.data.type_id == 1) {
            UX.boxes.dateBeforeBox.style.display = 'none';
            UX.boxes.dateAfterBox.style.display = 'none';
            UX.buttons.examBtn.style.display = 'none';
            advert.students.methods.setAdvert();
        }

        if(advert.students.data.department_id == 1) {
            UX.boxes.typesBox.style.display = 'block';
            document.getElementById('studentAdvert__controls--types').value = 1;
            advert.students.data.type_id = 1;
            advert.students.methods.setAdvert();
        } else {
            helpers.resetAdvert();
            UX.inputs.students.dateBefore.value = helpers.getTodayDate(1);
            UX.inputs.students.dateAfter.value = helpers.getTodayDate(2, 0);
			//console.log(helpers.getTodayDate(1));
		
            // let todayDate = new Date();
            // todayDate.setMonth(todayDate.getMonth() + 1);
            // const outputDate = todayDate.toLocaleDateString();
            // UX.inputs.students.dateAfter.value = String(outputDate).replace('.', '-');
            UX.boxes.dateBeforeBox.style.display = 'block';
            UX.boxes.dateAfterBox.style.display = 'block';
            // UX.buttons.examBtn.style.display = 'block';
            advert.students.data.dateFrom = UX.inputs.students.dateBefore.value;
            advert.students.data.dateTo = UX.inputs.students.dateAfter.value;

            advert.students.methods.setAdvert();
        }
    });

    // Type select
    UX.selects.students.types.addEventListener('change', function (e) {
        advert.students.data.type_id = e.target.value;

        if (advert.students.data.type_id == 'null') {
            helpers.resetAdvert();
            return false;
        }

        if(advert.students.data.type_id == 1) {
            advert.students.methods.setAdvert();
            UX.boxes.dateBeforeBox.style.display = 'none';
            UX.boxes.dateAfterBox.style.display = 'none';
            UX.buttons.examBtn.style.display = 'none';
        }
        else if (advert.students.data.type_id == 2) {
            helpers.resetAdvert();
            UX.inputs.students.dateBefore.value = helpers.getTodayDate(1);
            UX.inputs.students.dateAfter.value = helpers.getTodayDate(2, 0);
			//console.log(helpers.getTodayDate(2, 0));
            UX.boxes.dateBeforeBox.style.display = 'block';
            UX.boxes.dateAfterBox.style.display = 'block';
            // UX.buttons.examBtn.style.display = 'block';
            advert.students.data.dateFrom = UX.inputs.students.dateBefore.value;
            advert.students.data.dateTo = UX.inputs.students.dateAfter.value;

            advert.students.methods.setAdvert();
        }
        else if (advert.students.data.type_id == 3) {
            helpers.resetAdvert();
			UX.inputs.students.dateBefore.value = helpers.getTodayDate(1);
            UX.inputs.students.dateAfter.value = helpers.getTodayDate(2, 0);
			UX.boxes.dateBeforeBox.style.display = 'block';
            UX.boxes.dateAfterBox.style.display = 'block';
			advert.students.data.dateFrom = UX.inputs.students.dateBefore.value;
            advert.students.data.dateTo = UX.inputs.students.dateAfter.value;
			advert.students.methods.setAdvert();
        }
    });

    // // Show exam display
    // UX.buttons.examBtn.addEventListener('click', function (e) {
    //     e.preventDefault();
    //     advert.students.data.dateFrom = UX.inputs.students.dateBefore.value;
    //     advert.students.data.dateTo = UX.inputs.students.dateAfter.value;
    //
    //     advert.students.methods.setAdvert();
    // });

    UX.inputs.students.dateBefore.addEventListener('change', function (e) {
        advert.students.data.dateFrom = UX.inputs.students.dateBefore.value;
        advert.students.data.dateTo = UX.inputs.students.dateAfter.value;

        advert.students.methods.setAdvert();
    });

    UX.inputs.students.dateAfter.addEventListener('change', function (e) {
        advert.students.data.dateFrom = UX.inputs.students.dateBefore.value;
        advert.students.data.dateTo = UX.inputs.students.dateAfter.value;

        advert.students.methods.setAdvert();
    });

  /*   document.getElementById('printRasp').onclick = function (e) {
        var prtContent = document.getElementById("printable");
        var WinPrint = window.open('','','left=50,top=50,width=800,height=640,toolbar=0,scrollbars=1,status=0');
        WinPrint.document.write('<div id="print" class="contentpane">');
        WinPrint.document.write(prtContent.innerHTML);
        WinPrint.document.write('</div>');
        WinPrint.document.close();
        WinPrint.focus();
        WinPrint.print();
        WinPrint.close();
        prtContent.innerHTML=strOldOne;
    } */

};
