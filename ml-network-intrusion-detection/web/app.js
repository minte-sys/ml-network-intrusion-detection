const $=id=>document.getElementById(id);
$('analyze').addEventListener('click',async()=>{
  const file=$('file').files[0];
  if(!file){$('status').textContent='Select a CSV file first.';return}
  $('analyze').disabled=true;$('status').textContent='Analyzing traffic…';
  try{
    const form=new FormData();form.append('file',file);
    const response=await fetch('/predict-file',{method:'POST',body:form});
    const result=await response.json();
    if(!response.ok)throw Error(typeof result.detail==='string'?result.detail:'CSV validation failed');
    $('total').textContent=result.total.toLocaleString();$('normal').textContent=result.normal.toLocaleString();
    $('attack').textContent=result.attack.toLocaleString();$('percent').textContent=result.attack_percentage+'%';
    $('good').style.width=(100-result.attack_percentage)+'%';$('bad').style.width=result.attack_percentage+'%';
    $('alert').hidden=result.attack===0;
    $('alert').textContent=`⚠ Suspicious traffic detected: ${result.attack} of ${result.total} records classified as potentially malicious.`;
    $('rows').replaceChildren(...result.rows.slice(0,100).map(row=>{
      const tr=document.createElement('tr');
      for(const value of [row.record,row.prediction,Math.round(row.confidence*100)+'%']){
        const td=document.createElement('td');td.textContent=value;tr.append(td);
      }
      tr.className=row.prediction==='Attack'?'suspicious':'';return tr;
    }));
    $('status').textContent=`Analyzed ${result.total.toLocaleString()} records from ${file.name}.`;
  }catch(error){$('status').textContent=error.message}
  finally{$('analyze').disabled=false}
});
