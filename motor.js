/* Funciones puras compartidas por la interfaz y las comprobaciones. */
const Motor = (()=>{
 function random(){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]/4294967296;}
 function shuffle(xs,rng=random){const a=[...xs];for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
 function weighted(xs,rng=random){let n=rng()*xs.reduce((s,q)=>s+q.weight,0);for(const q of xs){n-=q.weight;if(n<0)return q;}return xs[xs.length-1];}
 function prepare(q,rng=random){const order=q.type==='mc'?shuffle([0,1,2,3],rng):[0,1];return {...q,options:order.map(i=>q.options[i]),answer:order.indexOf(q.answer)};}
 function exam(bank,seen=[],previous=[],rng=random){
  const chosen=[],usedConcepts=new Set(),seenSet=new Set(seen),prev=new Set(previous);let recycled=0;
  // 7 / 7 / 6 por capítulo; 4+4+4 de opción múltiple y 3+3+2 de V/F.
  for(const [chapter,type,count] of [[4,'mc',4],[5,'mc',4],[6,'mc',4],[4,'tf',3],[5,'tf',3],[6,'tf',2]]){
   for(let i=0;i<count;i++){
    const pool=bank.filter(q=>q.chapter===chapter&&q.type===type&&!usedConcepts.has(q.concept));
    const fresh=pool.filter(q=>!seenSet.has(q.id)&&!prev.has(q.id));
    const nonPrevious=pool.filter(q=>!prev.has(q.id));
    const available=fresh.length?fresh:nonPrevious.length?nonPrevious:pool;
    if(!available.length)throw Error('No hay suficientes conceptos para construir el intento.');
    const q=weighted(available,rng);if(seenSet.has(q.id))recycled++;
    chosen.push(prepare(q,rng));usedConcepts.add(q.concept);
   }
  }
  return {questions:shuffle(chosen,rng),recycled};
 }
 function score(questions,answers){let correct=0,wrong=0,blank=0;questions.forEach((q,i)=>{if(answers[i]==null)blank++;else if(answers[i]===q.answer)correct++;else wrong++;});return {correct,wrong,blank,total:questions.length};}
 function weaknesses(questions,answers){const map=new Map();questions.forEach((q,i)=>{let t=map.get(q.concept);if(!t){t={id:q.concept,title:q.topic,chapter:q.chapter,correct:0,wrong:0,blank:0};map.set(q.concept,t);}t[answers[i]==null?'blank':answers[i]===q.answer?'correct':'wrong']++;});return [...map.values()].filter(t=>t.wrong+t.blank>0).sort((a,b)=>(b.wrong+b.blank)-(a.wrong+a.blank));}
 function practice(bank,questions,answers,seen=[],rng=random){
  const missing=weaknesses(questions,answers),avoid=new Set(questions.map(q=>q.id)),seenSet=new Set(seen);let recycled=0;
  const result=missing.map(t=>{
   const candidates=bank.filter(q=>q.concept===t.id&&!avoid.has(q.id));
   const fresh=candidates.filter(q=>!seenSet.has(q.id));
   const q=weighted(fresh.length?fresh:candidates,rng);if(seenSet.has(q.id))recycled++;
   return prepare(q,rng);
  });return {questions:shuffle(result,rng),recycled};
 }
 function remaining(deadline,now=Date.now()){return Math.max(0,deadline-now);}
 return {shuffle,prepare,exam,score,weaknesses,practice,remaining};
})();
if(typeof module!=='undefined')module.exports=Motor;
