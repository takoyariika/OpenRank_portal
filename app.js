const $ = id => document.getElementById(id);
let catalog=null;
function add(tag, cls, content, parent){const el=document.createElement(tag);if(cls)el.className=cls;if(content!==undefined)el.textContent=String(content);if(parent)parent.append(el);return el;}
function render(){
 const results=$('results');results.replaceChildren();
 if(!catalog)return;
 const search=$('search').value.trim().toLowerCase();const mode=catalog.mode;
 const values=(mode==='directory'?catalog.portals:catalog.players)||[];
 const items=values.filter(item=>[item.title,item.name,item.repository,item.genre,item.game_id].filter(Boolean).join(' ').toLowerCase().includes(search));
 $('count').textContent=`${items.length}件`;
 if(!items.length){add('p','empty',search?'該当するデータはありません':'まだ公開データが収集されていません。ポータルのActionsを実行してください。',results);return;}
 items.forEach((item,index)=>{
  const link=add('a','card',undefined,results);
  link.href=item.page_url;link.target='_blank';link.rel='noopener noreferrer';
  add('div','avatar',mode==='directory'?'▦':String(index+1),link);
  const content=add('div',null,undefined,link);
  add('h2',null,mode==='directory'?item.title:item.name,content);
  add('p',null,mode==='directory'?`${item.game_id} · ${item.genre} · ${item.repository}`:`${item.repository} · ${item.wins}勝 ${item.losses}敗`,content);
  const value=add('div','score',undefined,link);
  if(mode==='directory'){add('strong',null,'↗',value);add('span',null,'ゲームポータル',value);}
  else {add('strong',null,item.rp,value);add('span',null,`RP · 勝率 ${item.win_rate.toFixed(1)}%`,value);}
 });
}
async function init(){
 try{
  const [cfgRes,res]=await Promise.all([fetch('portal.json'),fetch('data/catalog.json',{cache:'no-store'})]);
  if(!cfgRes.ok||!res.ok)throw Error('公開データを読み込めません');
  const config=await cfgRes.json(); catalog=await res.json();
  if(config.mode!==catalog.mode || (config.mode==='game'&&config.game_id!==catalog.game_id))throw Error('設定変更後の最初のクロールが必要です');
  $('title').textContent=config.title||'OpenRank';
  $('eyebrow').textContent=config.mode==='directory'?'OPENRANK / GAME DIRECTORY':`OPENRANK / ${config.genre||'GAME'} / ${config.game_id}`;
  $('summary').textContent=config.mode==='directory'?'誰でも立てられる、独立したゲーム別ランキングの一覧です。':'各プレイヤーのGitHub戦績から毎日集計されたランキングです。';
  if(!catalog.generated_at)$('status').textContent='初回集計待ち。Actions > daily crawl > Run workflow を実行してください。';
  render();
 }catch(e){$('status').textContent='読み込みに失敗: '+e.message;}
}
$('search').addEventListener('input',render);init();
