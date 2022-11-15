update patient_pressure set systole =  	regexp_match(dane_wpisu, 'BP \(mm/Hg\): ([\d]*)[ ]*/[ ]*[\d]*') where 1=1;
update patient_pressure set systole =  	regexp_replace(systole, '[{}]','','g') where 1=1;


update patient_pressure set diastole =  	regexp_match(dane_wpisu, 'BP \(mm/Hg\): [\d]*[ ]*/[ ]*([\d]*)') where 1=1;
update patient_pressure set diastole =  	regexp_replace(diastole, '[{}]','', 'g') where 1=1;


--select 1, 1, dane_wpisu, 	regexp_match(dane_wpisu, 'BMI[ ]*\[kg/m2\]:[ ]*([0-9,.]*)') from patient_pressure;

update patient_pressure set bmi =  	regexp_match(dane_wpisu, 'BMI[ ]*\[kg/m2\]:[ ]*([0-9,.]*)') where 1=1;
update patient_pressure set bmi =  	regexp_replace(bmi, '[{}"]','','g') where 1=1;
update patient_pressure set bmi =  	null where bmi='';


select "patientId", count(1) c from patient_pressure where "bmi" is not null  group by "patientId" order by c desc


select dane_wpisu from patient_pressure where dane_wpisu like '%c%'