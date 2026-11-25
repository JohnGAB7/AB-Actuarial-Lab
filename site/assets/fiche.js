  // Materialize common bare mathematical notation in prose, while preserving explicit TeX.
  const inlineNotation = (value) => {
    const pattern = /\b[A-Za-z]\([^()]{1,24}\)\^[A-Za-z0-9]+|\b[A-Za-z]_[A-Za-z0-9]+|\b[A-Za-z0-9)\]}]\^[A-Za-z0-9]+|\b[A-Za-z]\([^()]{1,24}\)/g;
    return String(value ?? "").split(/(\$[^$]*\$|\\\([^)]*\\\))/g).map((part,index) => {
      if (index % 2 === 1) return part;
      return part.replace(pattern, (match) => "$" + match + "$");
    }).join("");
  };
  const paragraph = (text) => make("p","",text);
  const formula = (text) => {
    const node = make("div","reference-formula");
    node.setAttribute("aria-label", text);
    if (window.katex) katex.render(text, node, {displayMode:true, throwOnError:false, strict:"ignore"});
    else node.textContent = text;
    return node;
  };
  const renderMath = (root) => {
    if (window.renderMathInElement) {
      window.renderMathInElement(root,{
        delimiters:[{left:"\\[",right:"\\]",display:true},{left:"\\(",right:"\\)",display:false},{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],
        throwOnError:false
      });
    }
  };
  const panelNodes = [];
  const renderers = [
    (data) => {
      const root=make("div","reference-panel");
      root.append(make("h2","",copy.tabs[0]));
      root.append(block(copy.question,paragraph(data.question)));
      root.append(block(copy.why,paragraph(data.pourquoi)));
      const grid=make("div","reference-grid");
      grid.append(block(copy.objectives,list(data.objectifs,true)));
      grid.append(block(copy.prerequisites,list(data.prerequis)));
      root.append(grid,block(copy.map,list(data.carte)));
      root.append(block(copy.duration,paragraph(data.duree_minutes+" min")));
      return root;
    },
    (data) => {
      const root=make("div","reference-panel");
      root.append(make("h2","",copy.tabs[1]));
      (data.sections||[]).forEach(section=>{
        const node=block(section.titre,paragraph(section.contenu));
        (section.formules||[]).forEach(item=>{
          node.append(formula(item.formule),paragraph(item.explication));
        });
        root.append(node);
      });
      return root;
    },
    (data) => {
      const root=make("div","reference-panel");
      root.append(make("h2","",copy.tabs[2]));
      (data.methodes||[]).forEach(method=>{
        const node=block(method.titre,paragraph(method.quand_utiliser));
        node.append(make("h3","",copy.steps),list(method.etapes,true));
        node.append(make("h3","",copy.checks),list(method.controles));
        node.append(make("h3","",copy.errors),list(method.erreurs));
        root.append(node);
      });
      return root;
    },
    (data) => {
      const root=make("div","reference-panel");
      root.append(make("h2","",copy.tabs[3]));
      (data.exemples||[]).forEach(example=>{
        const node=block(example.titre,paragraph(example.enonce));
        node.append(make("h3","",copy.reasoning),list(example.raisonnement,true));
        node.append(make("p","reference-result",example.resultat));
        node.append(make("h3","",copy.interpretation),paragraph(example.interpretation));
        node.append(make("h3","",copy.checks),list(example.controles));
        root.append(node);
      });
      return root;
    },
    (data) => {
      const root=make("div","reference-panel");
      root.append(make("h2","",copy.tabs[4]));
      (data.exercices||[]).forEach(exercise=>{
        const node=block(exercise.titre,paragraph(exercise.enonce));
        const level=make("span","eyebrow",exercise.niveau);
        node.append(level,make("h3","",copy.solution),list(exercise.corrige,true));
        node.append(make("h3","",copy.feedback),paragraph(exercise.feedback));
        root.append(node);
      });
      return root;
    },
    (data) => {
      const root=make("div","reference-panel");
      root.append(make("h2","",copy.tabs[5]));
      (data.applications||[]).forEach(app=>{
        const node=block(app.titre,paragraph(app.contexte));
        node.append(make("h3",,key==="procedure"));
        }
        root.append(node);
      });
      return root;
    },
    (data) => {
      const root=make("div","reference-panel");
      root.append(make("h2","",copy.tabs[6]));
      root.append(block(copy.memo,list(data.memo)));
      const table=make("table","reference-table");
      const head=make("thead");
      const row=make("tr");
      [lang==="en"?"French term":"Terme français",lang==="en"?"English term":"Terme anglais",lang==="en"?"Definition":"Définition"].forEach(x=>row.append(make("th","",x)));
      head.append(row);table.append(head);
      const body=make("tbody");
      (data.glossaire||[]).forEach(term=>{
        const tr=make("tr");
        [term.terme_fr,term.terme_en,term.definition].forEach(value=>tr.append(make("td","",value)));
        body.append(tr);
      });
      table.append(body);root.append(block(copy.glossary,table));
      const checklist=make("div","reference-check");
      (data.maitrise||[]).forEach((item,index)=>{
        const label=make("label","");
        const input=make("input","");
        input.type="checkbox";input.id="reference-check-"+index;
        label.append(input,make("span","",item));checklist.append(label);
      });
      root.append(block(copy.mastery,checklist));
      (data.references||[]).forEach(ref=>{
        const content=make("div","reference-reference");
        content.append(make("p","",ref.titre),paragraph(ref.detail));
        if(ref.url){
          try{
            const url=new URL(ref.url);
            if(url.protocol==="https:" && !url.username && !url.password){
              const a=make("a","",ref.url);a.href=url.href;a.target="_blank";a.rel="noopener noreferrer";
              content.append(a);
            }
          }catch{}
        }
        root.append(block(copy.references,content));
      });
      (data.liens||[]).forEach(link=>{
        // Translation overlays may translate labels, but must retain navigation targets.
        if(typeof link.cible!=="string" || !link.cible.includes("/") || typeof data.id!=="string") return;
        const a=make("a","reference-link",link.titre);
        const [target,anchor] = link.cible.split("#");
        const [targetDomain,targetSession] = target.split("/");
        const currentDomain = data.id.split("/")[0];
        const relative = targetDomain === currentDomain ? "../"+targetSession+"/index.html" : "../../"+targetDomain+"/"+targetSession+"/index.html";
        a.href=relative+(anchor?"#"+anchor:"");
        root.append(a);
      });
      return root;
    }
  ];
  const switcher=$("#lesson-mode"), steps=$("#lesson-pathway"), sheetNode=$("#reference-sheet");
  const tabs=$("#reference-tabs"), panels=$("#reference-panels");
  if(!switcher||!steps||!sheetNode||!tabs||!panels) return;
  switcher.hidden=false;
  $("#mode-steps").textContent=copy.modeSteps;
  $("#mode-reference").textContent=copy.modeSheet;
  $("#reference-kicker").textContent=copy.kicker;
  $("#reference-title").textContent=data.titre;
  $("#reference-notice").textContent=copy.notice;
  $("#reference-notice").className="reference-notice";

  const keys=["vue_ensemble","cours_complet","methodes","exemples_guides","exercices_corriges","applications_labs","synthese_references"];
  const tabButtons=[];
  keys.forEach((key,index)=>{
    const tab=make("button","",copy.tabs[index]);
    tab.type="button";tab.id="reference-tab-"+index;tab.setAttribute("role","tab");
    tab.setAttribute("aria-controls","reference-panel-"+index);
    tab.setAttribute("aria-selected",index===0?"true":"false");
    tab.tabIndex=index===0?0:-1;
    const panel=renderers[index](sheet[key]);
    panel.id="reference-panel-"+index;panel.setAttribute("role","tabpanel");
    panel.setAttribute("aria-labelledby",tab.id);panel.tabIndex=0;panel.hidden=index!==0;
    tab.addEventListener("click",()=>activate(index,true));
    tabs.append(tab);panels.append(panel);tabButtons.push(tab);panelNodes.push(panel);
  });
  let activeIndex=0;
  function activate(index,focus){
    activeIndex=index;
    tabButtons.forEach((tab,i)=>{
      tab.setAttribute("aria-selected",i===index?"true":"false");
      tab.tabIndex=i===index?0:-1;
      panelNodes[i].hidden=i!==index;
    });
    if(focus)tabButtons[index].focus();
    renderMath(panelNodes[index]);
  }
  tabs.addEventListener("keydown",event=>{
    const current=tabButtons.indexOf(document.activeElement);
    if(current<0)return;
    let next=current;
    if(event.key==="ArrowRight")next=(current+1)%tabButtons.length;
    else if(event.key==="ArrowLeft")next=(current-1+tabButtons.length)%tabButtons.length;
    else if(event.key==="Home")next=0;
    else if(event.key==="End")next=tabButtons.length-1;
    else return;
    event.preventDefault();activate(next,true);
  });
  function mode(reference){
    steps.hidden=reference;sheetNode.hidden=!reference;
    $("#mode-steps").setAttribute("aria-pressed",reference?"false":"true");
    $("#mode-reference").setAttribute("aria-pressed",reference?"true":"false");
    if(reference){
      // Reassert the selected tab when returning to reference mode. This prevents
      // a hidden panel from leaving the sheet blank after a mode transition.
      panelNodes.forEach((panel,index)=>{panel.hidden=index!==activeIndex;});
      renderMath(panelNodes[activeIndex]);
    }
  }
  $("#mode-steps").addEventListener("click",()=>mode(false));
  $("#mode-reference").addEventListener("click",()=>mode(true));
  renderMath(panelNodes[0]);
})();  // Materialize common bare mathematical notation in prose, while preserving explicit TeX.
  const inlineNotation = (value) => {
    const pattern = /\b[A-Za-z]\([^()]{1,24}\)\^[A-Za-z0-9]+|\b[A-Za-z]_[A-Za-z0-9]+|\b[A-Za-z0-9)\]}]\^[A-Za-z0-9]+|\b[A-Za-z]\([^()]{1,24}\)/g;
    return String(value ?? "").split(/(\$[^$]*\$|\\\([^)]*\\\))/g).map((part,index) => {
      if (index % 2 === 1) return part;
      return part.replace(pattern, (match) => "$" + match + "$");
    }).join("");
  };

