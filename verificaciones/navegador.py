"""Pruebas de interacción real; usar con el servidor local en el puerto 8000."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright, expect

OUT=Path(__file__).parent
KEY='cl3-practica-v1'
BASE='http://127.0.0.1:8000/'
checks=[]

def record(name):
    checks.append(name)
    print('PASS:',name,flush=True)

def stored(page,field='active'):
    return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',KEY)[field]

def correct(page):
    return page.evaluate("""(key)=>{
      const a=JSON.parse(localStorage.getItem(key)).active, entry=a.questions[a.index], q=BANCO.find(q=>q.id===entry.id);
      return entry.options.indexOf(q.options[q.answer]);
    }""",KEY)

def respond(page,value=None):
    before=stored(page)['index']
    if value is None:
        page.get_by_role('button',name='Dejar sin responder',exact=False).click()
    else:
        page.locator(f'.answer[data-answer="{value}"]').click()
    page.wait_for_function('(p)=>{const a=JSON.parse(localStorage.getItem(p.key)).active;return !a||a.index!==p.index}',arg={'key':KEY,'index':before})
    if before<19:
        expect(page.locator('#progress-label')).to_have_text(f'Pregunta {before+2} de 20')
    else:
        expect(page.locator('.score-circle')).to_be_visible()

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1365,'height':1000})
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.goto(BASE)
    expect(page.get_by_role('button',name='Comenzar',exact=False)).to_be_visible()
    page.screenshot(path=str(OUT/'inicio.png'),full_page=True)
    record('Pantalla inicial, instrucciones, distribución y referencias disponibles')
    page.get_by_role('button',name='Comenzar',exact=False).click()
    first=stored(page);first_ids=[q['id'] for q in first['questions']]
    expect(page.locator('#time')).to_have_text('10:00')
    expect(page.locator('.question-title')).to_have_count(1)
    assert page.locator('.feedback,.source').count()==0
    record('Comenzar activa 20 preguntas y reloj de 10 minutos, sin soluciones visibles')
    # 12 aciertos, 5 errores y 3 omisiones mediante botones reales.
    for i in range(20):
        a=correct(page)
        if i<12: respond(page,a)
        elif i<17:
            n=len(stored(page)['questions'][i]['options'])
            respond(page,(a+1)%n)
        else: respond(page)
        if i==0:
            expect(page.locator('.feedback,.source')).to_have_count(0)
    expect(page.locator('.score-circle')).to_contain_text('12/20')
    expect(page.locator('.stat').nth(0)).to_contain_text('12')
    expect(page.locator('.stat').nth(1)).to_contain_text('5')
    expect(page.locator('.stat').nth(2)).to_contain_text('3')
    assert page.locator('.review').count()==20
    record('Avance 1–20 y puntuación: 12 correctas, 5 incorrectas, 3 omisiones, 12/20')
    page.locator('.review summary').nth(12).click()
    expect(page.locator('.review[open] .wrong')).to_have_count(1)
    expect(page.locator('.review[open] .right')).to_have_count(1)
    expect(page.locator('.review[open] .source')).to_be_visible()
    expect(page.locator('.review[open] .explanation')).to_be_visible()
    page.locator('#filter').select_option('blank')
    expect(page.locator('.review')).to_have_count(3)
    page.locator('#filter').select_option('all')
    record('Revisión de respuesta propia, solución, explicación, referencias y filtros')
    page.screenshot(path=str(OUT/'resultado.png'),full_page=True)
    exam_result=stored(page,'last')
    page.get_by_role('button',name='Practicar mis errores',exact=True).click()
    practice=stored(page)
    assert len(practice['questions'])==8
    assert not set(first_ids)&{q['id'] for q in practice['questions']}
    expected={first['questions'][i]['id'].rsplit('-',1)[0] for i in range(12,20)}
    assert {q['id'].rsplit('-',1)[0] for q in practice['questions']}==expected
    expect(page.locator('[role=timer]')).to_have_count(0)
    i=practice['index'];a=correct(page);n=len(practice['questions'][i]['options'])
    page.locator(f'.answer[data-answer="{(a+1)%n}"]').click()
    expect(page.locator('.feedback')).to_contain_text('Incorrecto')
    expect(page.locator('.feedback .source')).to_be_visible()
    assert stored(page)['index']==0
    page.screenshot(path=str(OUT/'practica.png'),full_page=True)
    page.get_by_role('button',name='Siguiente pregunta',exact=False).click()
    expect(page.locator('#progress-label')).to_have_text('Pregunta 2 de 8')
    record('Práctica: preguntas nuevas de los 8 conceptos fallados u omitidos, sin reloj y con explicación inmediata')
    page.get_by_role('button',name='Terminar práctica',exact=True).click()
    expect(page.locator('#finish-dialog')).to_be_visible()
    page.get_by_role('button',name='Seguir practicando',exact=True).click()
    expect(page.locator('#progress-label')).to_have_text('Pregunta 2 de 8')
    page.get_by_role('button',name='Terminar práctica',exact=True).click()
    page.get_by_role('button',name='Finalizar y ver resultado',exact=True).click()
    assert stored(page,'last')==exam_result
    assert len(stored(page,'history'))==1
    record('Finalizar requiere confirmación; la práctica no altera la nota del control')
    page.get_by_role('button',name='Nueva simulación',exact=True).click()
    second=stored(page)
    assert not set(first_ids)&{q['id'] for q in second['questions']}
    record('Nueva simulación cambia las preguntas, no solo su orden')
    # Un reloj controlado permite verificar el límite completo sin esperar diez minutos.
    timed=browser.new_context(viewport={'width':390,'height':844})
    t=timed.new_page();t.on('pageerror',lambda e:errors.append(str(e)))
    t.clock.install()
    t.goto(BASE)
    t.get_by_role('button',name='Comenzar',exact=False).click()
    deadline=stored(t)['deadline']
    t.clock.fast_forward(31000)
    expect(t.locator('#progress-label')).to_have_text('Pregunta 1 de 20')
    expect(t.locator('#time')).to_have_text('9:29')
    record('Los 30 segundos no son un límite por pregunta')
    respond(t,correct(t))
    t.clock.fast_forward(1000)
    t.reload()
    expect(t.locator('#progress-label')).to_have_text('Pregunta 2 de 20')
    assert stored(t)['deadline']==deadline
    assert stored(t)['answers'][0] is not None
    record('Recarga restaura el avance y las respuestas sin reiniciar el plazo')
    respond(t,(correct(t)+1)%len(stored(t)['questions'][1]['options']))
    assert t.evaluate('document.documentElement.scrollWidth<=innerWidth')
    t.screenshot(path=str(OUT/'movil.png'),full_page=True)
    t.clock.fast_forward(569000)
    expect(t.locator('.score-circle')).to_contain_text('1/20')
    expect(t.locator('.stat').nth(0)).to_contain_text('1')
    expect(t.locator('.stat').nth(1)).to_contain_text('1')
    expect(t.locator('.stat').nth(2)).to_contain_text('18')
    expect(t.locator('.stat').nth(3)).to_contain_text('10:00')
    expect(t.locator('#app')).to_contain_text('Se agotaron los 10 minutos')
    assert stored(t) is None
    record('Agotamiento automático: 1 correcta, 1 incorrecta, 18 omisiones y 10:00 utilizados')
    record('Interfaz móvil sin desbordamiento horizontal')
    # Evitar doble registro incluso con dos eventos seguidos.
    t.get_by_role('button',name='Nueva simulación',exact=True).click()
    t.locator('.answer').first.evaluate('(b)=>{b.click();b.click()}')
    t.clock.fast_forward(200)
    expect(t.locator('#progress-label')).to_have_text('Pregunta 2 de 20')
    assert sum(x is not None for x in stored(t)['answers'])==1
    record('El doble clic no registra dos respuestas ni salta preguntas')
    # La aplicación funciona sin acceso externo después de cargarse.
    t.context.set_offline(True)
    respond(t,correct(t))
    expect(t.locator('#progress-label')).to_have_text('Pregunta 3 de 20')
    record('Botones y avance operativos sin red')
    assert not errors,errors
    record('Sin errores JavaScript en las sesiones verificadas')
    browser.close()
    (OUT/'navegador-resultados.json').write_text(json.dumps({'resultado':'PASS','comprobaciones':checks,'errores':errors},ensure_ascii=False,indent=2))
