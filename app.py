import json, sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from models.simulation_engine import PolicyInput, CATEGORY_CONFIG, calculate
from models.risk_model import assess
from models.efficiency_score import score
from utils.validation import validate_dataset
from utils.pdf_generator import build_report

ROOT = Path(__file__).parent
st.set_page_config(page_title="Gujarat Policy Simulator", page_icon="◈", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');
html,.stApp,section.main{color-scheme:light!important}.stApp{background:linear-gradient(140deg,#f5f9ff 0%,#f8fbf8 54%,#f6f4ff 100%);font-family:'DM Sans',sans-serif;color:#172b4d}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#082f49,#0e5673 58%,#0d796d);border-right:0}
[data-testid="stSidebar"] *{color:#f7fbff!important}[data-testid="stSidebar"] .stRadio label{padding:6px 9px;border-radius:8px;margin:2px 0}.stButton>button{border-radius:10px;font-weight:700;border:0;background:linear-gradient(100deg,#0b7189,#198754);color:#fff;padding:.55rem 1rem;box-shadow:0 6px 12px rgba(15,91,110,.16)}.stButton>button:hover{transform:translateY(-1px);background:linear-gradient(100deg,#075d73,#116e45);color:#fff}
.hero{position:relative;overflow:hidden;padding:3.2rem 3.3rem;background:linear-gradient(118deg,#062f4f 0%,#075f72 57%,#15906f 100%);color:white;border-radius:24px;box-shadow:0 18px 42px rgba(6,58,81,.22);margin-bottom:1.15rem}.hero:after{content:'◌  ◈  ◌';position:absolute;right:5%;top:21%;font-size:7.5rem;letter-spacing:.22em;opacity:.12}.hero h1{font-family:'Fraunces',serif;font-size:3rem;margin:0}.hero h3{font-size:1.25rem;font-weight:500;color:#c9f6e4;margin:.6rem 0}.hero p{max-width:700px;font-size:1.05rem;line-height:1.55;color:#e3f3f8}.eyebrow{display:inline-block;background:rgba(255,255,255,.17);border:1px solid rgba(255,255,255,.25);padding:.35rem .7rem;border-radius:99px;font-size:.78rem;font-weight:700;letter-spacing:.08em}.note{background:#fff8df;padding:13px 16px;border-radius:12px;border-left:5px solid #e4a11b;color:#654c12;margin:1rem 0 1.6rem}.info-card{background:#fff;padding:1.15rem;border-radius:16px;border:1px solid #e4edf3;box-shadow:0 7px 18px rgba(14,58,88,.07);min-height:130px}.info-card .icon{font-size:1.6rem}.info-card h4{margin:.35rem 0;color:#123b55}.info-card p{font-size:.88rem;line-height:1.4;color:#587080}.demo-card{background:linear-gradient(150deg,#ffffff,#ecf8f5);border:1px solid #cceadf;border-radius:16px;padding:1rem;min-height:158px}.demo-card .tag{color:#087c64;font-size:.72rem;font-weight:700;letter-spacing:.06em}.section-kicker{color:#13846e;font-weight:700;text-transform:uppercase;font-size:.78rem;letter-spacing:.1em}.stMetric{background:#fff;border:1px solid #e4edf3;border-radius:14px;padding:12px;box-shadow:0 5px 14px rgba(14,58,88,.05)}[data-testid="stMetric"],[data-testid="stMetric"] *{color:#123b55!important}[data-testid="stMetricLabel"] p{color:#5b7083!important;font-weight:600!important}[data-testid="stMetricValue"]{color:#123b55!important;font-weight:700!important}[data-testid="stMetricDelta"]{color:#087c64!important}section.main [data-testid="stWidgetLabel"] *,section.main [data-testid="stWidgetLabel"],section.main [data-testid="stRadio"] label,section.main [data-testid="stCheckbox"] label{color:#123b55!important;font-weight:600!important}section.main input,section.main textarea,section.main [data-baseweb="select"] span,section.main [data-baseweb="select"] input{color:#123b55!important;background-color:#fff!important}section.main [data-testid="stNumberInput"] button{background:#e8f3f4!important;color:#0b6570!important;border:1px solid #c8e3e0!important}h1,h2,h3{color:#123b55}.stTabs [data-baseweb="tab"]{font-weight:700}.stDataFrame{border-radius:12px;overflow:hidden}
/* Explicit light form theme: prevents Android/browser dark mode from hiding labels. */
label,label *,[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] *,[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{color:#123b55!important;font-weight:600!important}
[data-baseweb="select"] > div,[data-testid="stNumberInput"] [data-baseweb="input"],[data-testid="stTextInput"] [data-baseweb="input"]{background-color:#fff!important;border-color:#b9d3dd!important}
input,textarea,[data-baseweb="select"] span,[data-baseweb="select"] input{color:#123b55!important;background-color:transparent!important}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] label *{color:#f7fbff!important}
@media (max-width: 768px){
  .block-container{padding:1rem .8rem 3rem!important}
  .hero{padding:1.8rem 1.3rem;border-radius:18px}.hero:after{display:none}.hero h1{font-size:2.1rem;line-height:1.08}.hero h3{font-size:1.05rem}.hero p{font-size:.95rem}.eyebrow{font-size:.65rem;letter-spacing:.05em}
  h1{font-size:1.8rem!important}h2{font-size:1.4rem!important}h3{font-size:1.15rem!important}
  [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.7rem!important}
  [data-testid="column"]{flex:1 1 calc(50% - .7rem)!important;min-width:calc(50% - .7rem)!important}
  .stButton>button{width:100%;min-height:46px;font-size:1rem}.stMetric{padding:10px}.note{font-size:.88rem;margin: .8rem 0 1.2rem}
  .info-card,.demo-card{min-height:0;padding:1rem}.stSlider{padding-top:.4rem}.stSelectbox,.stNumberInput{margin-bottom:.75rem}
}
@media (max-width: 480px){
  [data-testid="column"]{flex-basis:100%!important;min-width:100%!important}
  .hero{padding:1.5rem 1.05rem}.hero h1{font-size:1.85rem!important}.hero h3{font-size:1rem!important}
  [data-testid="stSidebar"]{min-width:0}.stMarkdown p{font-size:.95rem}
}
</style>""", unsafe_allow_html=True)

@st.cache_data
def districts(): return pd.read_csv(ROOT / "data" / "districts.csv")

def db():
    con=sqlite3.connect(ROOT / "policy_simulator.db")
    con.execute("CREATE TABLE IF NOT EXISTS scenarios (id INTEGER PRIMARY KEY, name TEXT, category TEXT, created TEXT, districts TEXT, cost REAL, efficiency REAL, risk REAL, payload TEXT)")
    return con
def save_scenario(inp, result, eff, risk):
    con=db(); con.execute("INSERT INTO scenarios(name,category,created,districts,cost,efficiency,risk,payload) VALUES(?,?,?,?,?,?,?,?)",(inp.name,inp.category,datetime.now().strftime('%Y-%m-%d %H:%M'),json.dumps(inp.districts),result['financial']['proposed_cost'],eff['total'],risk['score'],json.dumps(inp.to_dict()))); con.commit(); con.close()
def load_scenarios():
    con=db(); df=pd.read_sql_query("SELECT * FROM scenarios ORDER BY id DESC",con); con.close(); return df
def money(x): return f"₹{x/10_000_000:,.2f} Cr" if abs(x)>=10_000_000 else f"₹{x:,.0f}"
def selected_data(names): return districts()[districts().district.isin(names)]
def run(inp):
    result=calculate(inp, selected_data(inp.districts)); risk=assess(result['financial'], result['beneficiaries'], result['impact'], result['impact']['readiness']); eff=score(result['financial'],result['beneficiaries'],result['impact'],risk); return result,risk,eff
def demo_input(name):
    rows=pd.read_csv(ROOT/'data'/'sample_policy_data.csv'); r=rows[rows.policy_name==name].iloc[0]
    return PolicyInput(name, r.category, districts().district.tolist(), float(r.current_benefit),float(r.proposed_benefit),int(r.current_beneficiaries),int(r.proposed_beneficiaries),3,4,float(r.duration_years))
def show_results(inp,result,risk,eff):
    f,b,im=result['financial'],result['beneficiaries'],result['impact']
    st.subheader("Simulation results")
    st.caption("Estimated outputs from transparent inputs and synthetic demo data — not official forecasts.")
    c=st.columns(5); c[0].metric("Proposed cost",money(f['proposed_cost']),money(f['additional_cost'])+" vs current"); c[1].metric("Beneficiaries",f"{b['proposed']:,}",f"+{b['additional']:,}"); c[2].metric("Cost / beneficiary",money(f['cost_per_beneficiary'])); c[3].metric("Estimated impact",f"{im['score']}/100"); c[4].metric("Efficiency score",f"{eff['total']}/100")
    st.info(f"Scenario range for proposed cost: **{money(f['range_low'])}–{money(f['range_high'])}** (10th–90th percentile across stated assumption variations; not a confidence interval).")
    left,right=st.columns([1.05,1]);
    with left:
        st.markdown("#### Financial & beneficiary impact")
        chart=pd.DataFrame({"Measure":["Current cost","Proposed cost"],"Rupees":[f['current_cost'],f['proposed_cost']]}); st.plotly_chart(px.bar(chart,x="Measure",y="Rupees",text_auto='.3s',color="Measure",color_discrete_sequence=['#8ab6c9','#0b4f6c']),use_container_width=True)
        st.markdown("**Formula:** benefit × beneficiaries × duration. Additional cost = proposed − current.")
    with right:
        st.markdown("#### Explainable impact proxies")
        radar=go.Figure(go.Scatterpolar(r=[im['reach'],im['affordability'],im['access']],theta=["Reach","Affordability","Access"],fill='toself',line_color='#157a8a')); radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])),showlegend=False,height=300); st.plotly_chart(radar,use_container_width=True)
        st.caption(f"Readiness modifier: {im['readiness']:.2f}, based on selected synthetic district capacity. These are not causal predictions.")
    st.markdown("#### Risks and trade-offs")
    for title,level,detail in risk['items']: st.warning(f"**{level} — {title}:** {detail}")
    for good in risk['positives']: st.success(good)
    st.markdown("#### Policy Efficiency Score")
    scores=pd.DataFrame({"Component":["Financial efficiency","Beneficiary reach","Expected impact","Risk management"],"Score":[eff['financial'],eff['reach'],eff['impact'],eff['risk']]}); st.plotly_chart(px.bar(scores,x="Score",y="Component",orientation='h',range_x=[0,100],color="Score",color_continuous_scale="Teal"),use_container_width=True)
    st.caption("Weighted score: 30% financial efficiency, 25% reach, 25% expected impact, 20% risk management. It is based on selected assumptions and model parameters.")
    with st.expander("Inputs, assumptions, and why this result changed"):
        st.json(inp.to_dict()); st.write("**Assumptions**"); [st.write("• "+x) for x in result['assumptions']]; st.write(f"Cost changes mainly because the unit benefit changed by {result['changes']['benefit_pct']:.1f}% and beneficiary count changed by {b['change_pct']:.1f}%.")
    st.download_button("Download PDF report",build_report(inp.to_dict(),result,eff,risk),file_name=f"{inp.name.replace(' ','_')}_report.pdf",mime="application/pdf")

def simulation_page():
    st.title("New simulation")
    st.caption("All bundled district data is **Demo/Synthetic Data**.")
    category=st.selectbox("1. Select policy category",list(CATEGORY_CONFIG)); benefit_label, person_label, _=CATEGORY_CONFIG[category]
    geography=st.radio("2. Select geography",["Gujarat-wide","Select districts"],horizontal=True)
    names=districts().district.tolist() if geography=="Gujarat-wide" else st.multiselect("Districts",districts().district.tolist(),default=["Ahmedabad","Surat"])
    if not names: st.error("Select at least one district."); return
    st.markdown("### 3–4. Define policy values")
    a,b=st.columns(2)
    with a:
        st.markdown("**Current policy**"); current_benefit=st.number_input("Current "+benefit_label,min_value=0.0,value=10000.0,step=500.0); current_people=st.number_input("Current "+person_label,min_value=1,value=200000,step=1000); current_threshold=st.number_input("Current eligibility threshold (₹ lakh)",min_value=0.0,value=3.0,step=.5)
    with b:
        st.markdown("**Proposed policy / What-if controls**"); proposed_benefit=st.slider("Proposed "+benefit_label,0,50000,15000,500); proposed_people=st.slider("Proposed "+person_label,1000,1000000,220000,1000); proposed_threshold=st.slider("Proposed eligibility threshold (₹ lakh)",.0,10.0,4.0,.5)
    duration=st.slider("Policy duration (years)",.5,5.0,1.0,.5); name=st.text_input("Scenario name",f"{category} policy scenario")
    inp=PolicyInput(name,category,names,current_benefit,proposed_benefit,current_people,proposed_people,current_threshold,proposed_threshold,duration)
    if st.button("Run simulation",type="primary",use_container_width=True): st.session_state['active']=(inp,)+run(inp)
    if 'active' in st.session_state:
        active=st.session_state['active']; show_results(*active)
        if st.button("Save scenario to library"): save_scenario(*active); st.success("Scenario saved.")

def dashboard():
    st.markdown("<div class='hero'><span class='eyebrow'>GUJARAT • POLICY INTELLIGENCE • DEMO MODE</span><h1>Gujarat Policy Simulator</h1><h3>Test the Policy Before Testing It on People.</h3><p>Explore policy choices before implementation with clear cost estimates, beneficiary reach, explainable impact indicators, district comparisons and risk trade-offs.</p></div>",unsafe_allow_html=True)
    st.markdown("<div class='note'>Simulation results are estimates generated from available data and assumptions. They are intended to support policy analysis and should not be treated as official government forecasts or decisions.</div>",unsafe_allow_html=True)
    df=load_scenarios(); c=st.columns(4); c[0].metric("Total simulations",len(df)); c[1].metric("Estimated government cost",money(df.cost.sum()) if len(df) else "—"); c[2].metric("Estimated beneficiaries","Demo mode ready"); c[3].metric("Average efficiency",f"{df.efficiency.mean():.1f}/100" if len(df) else "—")
    st.markdown("<p class='section-kicker'>Try it instantly</p><h2>Start with a demo policy</h2>",unsafe_allow_html=True)
    cols=st.columns(4)
    for col,name in zip(cols,pd.read_csv(ROOT/'data'/'sample_policy_data.csv').policy_name):
        with col:
            icon={'Higher Education Scholarship':'🎓','Public Transport Fare Reduction':'🚌','Healthcare Coverage Expansion':'🩺','Skill Development Subsidy':'🛠️'}[name]
            st.markdown(f"<div class='demo-card'><div class='tag'>READY-TO-RUN SCENARIO</div><h3>{icon} {name}</h3><p>Open, adjust the policy controls and compare the estimated trade-offs.</p></div>",unsafe_allow_html=True)
            if st.button("Run",key=name):
                inp=demo_input(name); st.session_state['active']=(inp,)+run(inp); st.session_state['page']='New Simulation'; st.session_state['nav_page']='New Simulation'; st.rerun()
    st.markdown("<br><p class='section-kicker'>Decision pathway</p><h2>From public spending to public value</h2>",unsafe_allow_html=True)
    features=st.columns(4)
    cards=[('💰','Cost & budget','See current cost, proposed cost, additional expenditure and a scenario range.'),('👥','Reach & beneficiaries','Understand who may be covered and how beneficiary reach changes.'),('🗺️','District intelligence','Compare synthetic district-level capacity, impact, efficiency and risk.'),('⚠️','Risk & trade-offs','Flag budget pressure, workload and delivery capacity before action.')]
    for col,(icon,title,text) in zip(features,cards):
        col.markdown(f"<div class='info-card'><div class='icon'>{icon}</div><h4>{title}</h4><p>{text}</p></div>",unsafe_allow_html=True)
    st.markdown("<br><div style='background:linear-gradient(90deg,#e7f6f2,#edf5ff);border-radius:16px;padding:18px 22px;border:1px solid #d7eae7'><b style='color:#0b6b65'>DON'T ASK ONLY: WHAT WILL THIS POLICY COST?</b><br><span style='font-size:1.15rem;color:#173f56'>Ask what impact every ₹1 crore of public spending could create.</span></div>",unsafe_allow_html=True)

def library():
    st.title("Policy scenarios"); df=load_scenarios()
    if df.empty: st.info("No saved scenarios yet. Run a simulation and save it here."); return
    display=df[['id','name','category','created','districts','cost','efficiency','risk']].copy(); display['cost']=display.cost.map(money); st.dataframe(display,use_container_width=True,hide_index=True)
    pick=st.selectbox("Open or delete scenario",df.id,format_func=lambda x: df[df.id==x].name.iloc[0])
    col1,col2=st.columns(2)
    if col1.button("Open selected"):
        row=df[df.id==pick].iloc[0]; payload=json.loads(row.payload); inp=PolicyInput(**payload); st.session_state['active']=(inp,)+run(inp); st.session_state['page']='New Simulation'; st.session_state['nav_page']='New Simulation'; st.rerun()
    if col2.button("Delete selected"):
        con=db(); con.execute("DELETE FROM scenarios WHERE id=?",(int(pick),)); con.commit(); con.close(); st.rerun()

def comparison():
    st.title("Compare policies"); df=load_scenarios()
    if len(df)<2: st.info("Save at least two scenarios to compare them."); return
    ids=st.multiselect("Scenarios",df.id.tolist(),default=df.id.head(3).tolist(),format_func=lambda x: df[df.id==x].name.iloc[0])
    out=[]
    for i in ids:
        r=df[df.id==i].iloc[0]; out.append({'Policy':r['name'],'Government cost':r.cost,'Efficiency score':r.efficiency,'Risk score':r.risk})
    comp=pd.DataFrame(out); st.dataframe(comp.style.format({'Government cost':money,'Efficiency score':'{:.1f}','Risk score':'{:.1f}'}),use_container_width=True,hide_index=True)
    st.plotly_chart(px.bar(comp,x='Policy',y=['Efficiency score','Risk score'],barmode='group',range_y=[0,100]),use_container_width=True)
    recommended=comp.sort_values(['Efficiency score','Risk score'],ascending=[False,True]).iloc[0]; st.success(f"**Model-based recommendation: {recommended['Policy']}** — highest selected efficiency with lower risk as a tie-breaker. This does not replace expert, legal, financial, or policy review.")

def map_page():
    st.title("Gujarat district analysis")
    st.caption("This is a district comparison visualization using Demo/Synthetic Data; it is not a geographic boundary map.")
    inp=st.session_state.get('active',(demo_input('Higher Education Scholarship'),))[0]; result,risk,eff=run(inp); dd=pd.DataFrame(result['districts'])
    metric=st.selectbox("Colour districts by",['impact','efficiency','risk','beneficiaries','cost'])
    st.plotly_chart(px.scatter(dd,x='efficiency',y='impact',size='beneficiaries',color=metric,hover_name='district',text='district',color_continuous_scale='Teal',size_max=55),use_container_width=True)
    district=st.selectbox("District profile",dd.district); r=dd[dd.district==district].iloc[0]; st.write(f"**{district} — Demo/Synthetic Data**"); st.json({'estimated_beneficiaries':int(r.beneficiaries),'estimated_cost':money(r.cost),'estimated_impact_score':r.impact,'risk_score':r.risk,'efficiency_score':r.efficiency})

def analytics():
    st.title("Analytics & sensitivity")
    inp=st.session_state.get('active',(demo_input('Higher Education Scholarship'),))[0]; result,risk,eff=run(inp); f=result['financial']
    st.subheader("Government cost sensitivity")
    sens=pd.DataFrame({'Variable':['Benefit amount','Beneficiary count','Duration','Eligibility threshold'],'Influence':[.45,.40,.12,.03],'Level':['Very High','Very High','High','Medium']}); st.plotly_chart(px.bar(sens,x='Influence',y='Variable',orientation='h',text='Level',range_x=[0,.5],color='Influence',color_continuous_scale='Blues'),use_container_width=True)
    st.caption("Sensitivity is derived from the financial formula: cost = benefit × beneficiaries × duration. Eligibility threshold affects take-up only indirectly in this prototype.")
    st.subheader("District beneficiary distribution"); st.plotly_chart(px.bar(pd.DataFrame(result['districts']).sort_values('beneficiaries',ascending=False),x='district',y='beneficiaries'),use_container_width=True)

def data_sources():
    st.title("Data sources & upload")
    st.warning("**Demo/Synthetic Data:** Bundled district population, household, capacity and development inputs are realistic-looking synthetic values for demonstration. They are not government records.")
    st.markdown("**Real/Public Data (future integration):** replace local CSVs only with documented sources, year, methodology and licensing, such as departmental administrative data or published government/open-data releases. Validate before modelling.")
    st.dataframe(pd.DataFrame([['district','District name','Demo/Synthetic Data','2026','text'],['population','Population proxy','Demo/Synthetic Data','2026','people'],['capacity_index','Service delivery readiness proxy','Demo/Synthetic Data','2026','0–1']],columns=['Variable','Meaning','Source','Year','Unit']),hide_index=True,use_container_width=True)
    upload=st.file_uploader("Admin data upload — CSV or Excel",type=['csv','xlsx'])
    if upload:
        try:
            new=pd.read_csv(upload) if upload.name.endswith('.csv') else pd.read_excel(upload); findings=validate_dataset(new,districts().district.tolist())
            if findings: st.error("Data-quality report: " + " | ".join(findings))
            else: st.success(f"Data-quality report: passed {len(new)} rows. Review source, year, and methodology before using it in production."); st.dataframe(new.head(),use_container_width=True)
        except Exception as e: st.error(f"Could not read this file safely: {e}")

def reports():
    st.title("Reports")
    st.caption("Generate a printable decision-support report for the active scenario.")
    if 'active' not in st.session_state:
        st.info("Run a simulation or open a saved scenario first."); return
    inp,result,risk,eff=st.session_state['active']
    st.write(f"**{inp.name}** · {inp.category} · {', '.join(inp.districts)}")
    st.download_button("Download professional PDF report",build_report(inp.to_dict(),result,eff,risk),file_name=f"{inp.name.replace(' ','_')}_report.pdf",mime="application/pdf",type="primary")
    st.markdown("The report includes current/proposed policy, financial and beneficiary estimates, assumptions, risks, efficiency score, limitations, and the required disclaimer.")

PAGES={'Dashboard':dashboard,'New Simulation':simulation_page,'Policy Scenarios':library,'Compare Policies':comparison,'Gujarat Map':map_page,'Analytics':analytics,'Reports':reports,'Data Sources':data_sources,'About':lambda: st.markdown("## About\nA transparent local decision-support prototype for Gujarat policy exploration. It intentionally avoids official branding and claims of predictive certainty.")}
if 'page' not in st.session_state: st.session_state['page']='Dashboard'
if 'nav_page' not in st.session_state: st.session_state['nav_page']=st.session_state['page']
def change_page(): st.session_state['page']=st.session_state['nav_page']
with st.sidebar:
    st.title("◈ GPS")
    st.caption("DEMO MODE • Synthetic data")
    st.caption("Tap a page below to open it.")
    st.radio("Navigation",list(PAGES),key='nav_page',on_change=change_page)
    st.divider(); st.caption("Cost → Reach → Impact → Risk → Efficiency")
PAGES[st.session_state['page']]()
