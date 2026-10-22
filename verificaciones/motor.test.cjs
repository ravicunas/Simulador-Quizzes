const assert=require('node:assert/strict');
const {BANCO,CONCEPTOS,FUENTES}=require('../banco.js');
const Motor=require('../motor.js');
let checks=0;
function check(value,message){assert.ok(value,message);checks++;}
check(BANCO.length===180,'El banco tiene 180 preguntas.');
check(new Set(BANCO.map(q=>q.id)).size===BANCO.length,'Identificadores únicos.');
for(const q of BANCO){
 check(q.options.length===(q.type==='mc'?4:2),q.id+' alternativas');
 check(new Set(q.options).size===q.options.length,q.id+' sin alternativas duplicadas');
 check(Number.isInteger(q.answer)&&q.answer>=0&&q.answer<q.options.length,q.id+' respuesta válida');
 check(q.explanation.length>40,q.id+' explicación sustantiva');
 check(q.refs.length>0&&q.refs.every(r=>FUENTES[r.file]&&r.loc),q.id+' fuentes');
 if(q.type==='tf'&&q.answer===1)check(/Corrección:/.test(q.explanation),q.id+' corrige toda afirmación falsa');
}
let seen=[],previous=[];const positions=[0,0,0,0];let recycled=0;
for(let run=0;run<1000;run++){
 const e=Motor.exam(BANCO,seen,previous),qs=e.questions;
 check(qs.length===20,'20 preguntas');
 check(qs.filter(q=>q.type==='mc').length===12,'12 de opción múltiple');
 check(qs.filter(q=>q.type==='tf').length===8,'8 de V/F');
 check(qs.filter(q=>q.chapter===4).length===7&&qs.filter(q=>q.chapter===5).length===7&&qs.filter(q=>q.chapter===6).length===6,'Cobertura 7/7/6');
 check(new Set(qs.map(q=>q.concept)).size===20,'Sin repetir concepto dentro del intento');
 check(qs.every(q=>!previous.includes(q.id)),'No repetir preguntas del intento anterior');
 qs.forEach(q=>{const base=BANCO.find(x=>x.id===q.id);check(q.options[q.answer]===base.options[base.answer],'La mezcla conserva la solución');if(q.type==='mc')positions[q.answer]++;});
 const ans=qs.map((q,i)=>i<12?q.answer:i<17?(q.answer+1)%q.options.length:null);
 assert.deepEqual(Motor.score(qs,ans),{correct:12,wrong:5,blank:3,total:20});checks++;
 const practice=Motor.practice(BANCO,qs,ans,seen).questions;
 check(practice.length===8,'8 conceptos errados u omitidos');
 check(practice.every(q=>!qs.some(x=>x.id===q.id)),'La práctica usa preguntas distintas a las del control');
 check(practice.every(q=>qs.some((x,i)=>x.concept===q.concept&&ans[i]!==x.answer)),'Práctica del concepto fallado');
 check(Motor.practice(BANCO,qs,qs.map(q=>q.answer),seen).questions.length===0,'Sin errores no se inventa una práctica');
 recycled+=e.recycled;seen=[...new Set([...seen,...qs.map(q=>q.id)])];previous=qs.map(q=>q.id);
}
check(positions.every(n=>n>2500&&n<3500),'La posición de la respuesta correcta varía sin sesgo notable');
check(recycled>0,'Se informa de reutilización al agotar el banco');
check(Motor.remaining(1000,999)===1&&Motor.remaining(1000,1001)===0,'Cierre del reloj');
console.log(JSON.stringify({checks,simulaciones:1000,preguntas:BANCO.length,conceptos:CONCEPTOS.length,posicionesCorrectas:positions,resultado:'PASS'},null,2));
