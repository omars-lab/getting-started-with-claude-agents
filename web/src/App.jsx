// The "Getting Started with Claude Agents" web guide, as a Vite + React app.
//
// Ported from the prior htm single-file template. A <Mockup> from @omars-lab/blog-ui
// (installed from GitHub Packages) is rendered in the "Getting started" section, so this
// page doubles as a live, cross-repo proof that the package is consumable by a real bundler.
// (The reader-facing "agent in motion" beat is the terminal GIF below it; the scripted
// Walkthrough was removed as redundant.)
import {useState, useEffect, Fragment} from 'react';
import {Mockup} from '@omars-lab/blog-ui';
import '@omars-lab/blog-ui/style.css';
import './guide.css';

import finderHidden from './assets/finder-hidden.svg';
import finderShown from './assets/finder-shown.svg';
import finderClaude from './assets/finder-claude.svg';
import finderAgents from './assets/finder-agents.svg';
import finderSkills from './assets/finder-skills.svg';
import claudeAgents from './assets/claude-agents.svg';
import claudeSplash from './assets/claude-splash.svg';
import spotlight from './assets/spotlight.svg';
import terminalGif from './assets/terminal.gif';

// skill chips → one-line summary (distilled from each SKILL.md description)
const SKILLS = {
  'ensure-deps':          ['Pre-flight check', "Runs first. Verifies the Python venv, dependencies, LibreOffice, and a writable agent-outputs/ before any real work, and stops with fixes if something's missing."],
  'ticker-discovery':     ['Daily catalyst sweep', 'Surfaces 3–7 names worth a look today by scanning news, earnings, analyst actions, and unusual price/volume moves.'],
  'stock-discovery':      ['Raw setup sweep', 'Scans SEC filings (Form 4, 13F, 8-K, S-1), options, and politician trades for names matching specific setups, pure data, no judgment.'],
  'hidden-opportunities': ["The asymmetry filter", "Takes a candidate list and surfaces the 3–5 names where consensus isn't looking yet, plus what it deliberately dismissed."],
  'ticker-data':          ['Source-of-truth fetch', 'Pulls filings, quote, 2-year prices, news, and peers for one ticker and caches them, so later skills read instead of re-fetching.'],
  'stock-analysis':       ['The qualitative read', 'Builds the one-page understanding: business snapshot, recent news, peer context, and the key debates worth knowing today.'],
  'growth-study':         ['The model', 'Spreads revenue and growth (MoM/QoQ/YoY) into a 3-tab Excel workbook, Fundamentals, News, Historical, referenced by the report.'],
  'xlsx-author':          ['Shared workbook discipline', 'The conventions every spreadsheet follows: formulas (never hardcoded results), each input commented with its source. Reused by growth-study.'],
  'thesis-stress-test':   ['The validation step', "Runs 'what if X happens' scenarios against the thesis, surfaces falsifiable claims, and steelmans the bear case before anything is presented."],
  'explain-agent':        ['Self-explanation', 'Generates an interactive HTML diagram of how the agent works, which skill fires when, what data flows where, which guardrails apply.'],
};

// ---- FieldNoteRow: the .row + .note gutter layout used by most sections.
function FieldNoteRow({label, hint, children}) {
  return (
    <div className="wrap row">
      <aside className="note"><b>{label}</b>{hint}</aside>
      <div>{children}</div>
    </div>
  );
}

// ---- Hero: the header/hero incl. the TOC nav.
function Hero() {
  return (
    <header className="hero">
      <div className="wrap">
        <p className="eyebrow">A field guide to one working agent</p>
        <h1>Meet the<br/>Stock Analyzer Agent.</h1>
        <p className="lede">You know how a research desk works. This folder turns that
          knowledge into a working Claude Code agent, and it's built to be
          <em> read</em>, not just run. Ten minutes here and the question
          <em> "what even is an agent?"</em> answers itself.</p>
        <div className="stamp"><span className="dot"></span> No code required to read along · macOS · open offline</div>
        <nav className="toc">
          <a href="#big-idea">The big idea</a>
          <a href="#need">Before we begin</a>
          <a href="#open">Open it</a>
          <a href="#reveal">Reveal .claude</a>
          <a href="#anatomy">Inside .claude</a>
          <a href="#run">Getting started</a>
          <a href="#io">Inputs & outputs</a>
          <a href="#next">Make it yours</a>
          <a href="#deploy">Where it runs</a>
        </nav>
      </div>
    </header>
  );
}

// ---- Card: the .card who/how cards.
function Card({kind, tag, title, sub, children}) {
  return (
    <div className={'card ' + kind}>
      {tag}
      <h3>{title}</h3>
      {sub ? <div className="sub">{sub}</div> : null}
      {children}
    </div>
  );
}

// ---- SkillCard: the CYCLING skill card.
function SkillCard() {
  const names = Object.keys(SKILLS);
  const [i, setI] = useState(0);
  const [fade, setFade] = useState(false);

  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const id = setInterval(() => {
      if (reduce) {
        setI(prev => (prev + 1) % names.length);
        return;
      }
      setFade(true);
      setTimeout(() => {
        setI(prev => (prev + 1) % names.length);
        setFade(false);
      }, 450);
    }, 2600);
    return () => clearInterval(id);
  }, []);

  const n = names[i];
  const role = SKILLS[n][0], desc = SKILLS[n][1];

  return (
    <div className="card how">
      <span className="tag">The how · skill <span className="cyclehint">· cycling through 10</span></span>
      <div id="skillcycle" className={'cyclebody' + (fade ? ' fade' : '')}>
        <h3 id="cyc-name">{n}</h3>
        <div className="sub" id="cyc-path">{'.claude/skills/' + n + '/SKILL.md'}</div>
        <p id="cyc-desc"><b>{role + '.'}</b> {' ' + desc}</p>
      </div>
      <div className="cycdots" id="cyc-dots" aria-hidden="true">
        {names.map((nm, k) => <span key={k} className={nm === n ? 'on' : ''}></span>)}
      </div>
    </div>
  );
}

// ---- BigIdea section
function BigIdea() {
  return (
    <section id="big-idea">
      <FieldNoteRow label="start here" hint="one sentence to hang everything else on">
        <h2>An agent is a who. A skill is a how.</h2>
        <p>That's the whole mental model, and it holds for <em>any</em> agent, in any
          domain. You give the agent a <b>goal</b>; it leverages its <b>skills</b>,
          sets of instructions, to reach it.</p>
        <div className="split">
          <Card kind="who" tag={<span className="tag">The who · agent</span>} title="A role, given an objective">
            <p>Agents are <b>role-focused</b>. You hand one a <b>goal</b>, an
              objective, not step-by-step orders, and it decides <em>what to do
              next</em> to get there. They work best kept narrow: one clear domain,
              not a do-everything assistant.</p>
            <ul className="exlist">
              <li><b>A developer agent</b> → "ship the feature, keep tests green"</li>
              <li><b>A researcher agent</b> → "find what's worth a closer look today"</li>
              <li><b>A tester agent</b> → "break it before users do"</li>
            </ul>
          </Card>
          <Card kind="how" tag={<span className="tag">The how · skill</span>} title="A set of instructions">
            <p>Skills are <b>sets of instructions</b> for one task, the recipe, the
              procedure, the steps and standards for doing a specific thing well.
              Each is small, self-contained, and reusable across agents.</p>
            <ul className="exlist">
              <li>The developer's: <b>run-migrations</b>, <b>open-a-PR</b></li>
              <li>The researcher's: <b>pull-filings</b>, <b>build-a-workbook</b></li>
              <li>The tester's: <b>write-fuzz-cases</b>, <b>diff-snapshots</b></li>
            </ul>
          </Card>
        </div>
        <div className="split vs-split">
          <div className="vs-col who">↑ WHO DECIDES</div>
          <div className="vs-col how">HOW EXECUTES ↑</div>
        </div>
        <div className="keylines">
          <p className="keyline"><mark>Agents decide what skills they use to accomplish an objective.</mark></p>
          <p className="keyline"><mark>Skills instruct agents on how to properly leverage tools.</mark>
            <span className="keynote"> how to call an API, what to do with its response,
            which file format to write, when to stop.</span></p>
        </div>
        <p style={{marginTop: '18px'}}>The agent reads its own definition, then reaches
          for skills as the work calls for them. Skills generally don't know about
          each other, which is exactly why you can copy one into another agent or
          rewrite it without touching the rest.</p>

        <h3 style={{margin: '34px 0 4px', fontSize: '18px'}}>What this guide walks through</h3>
        <p style={{color: 'var(--ink-soft)', marginBottom: '14px'}}>In this guide we'll walk through
          how a <b>stock-analysis agent</b> was configured and given <b>10 different skills</b>,
          and how it uses them to turn a morning market scan into a research report. The
          same who/how idea, made concrete: one researcher agent and its ten abilities.</p>
        <div className="split">
          <Card kind="who" tag={<span className="tag">The who · agent</span>} title="stock-analyzer" sub=".claude/agents/stock-analyzer.md">
            <p>The role: "a desk-side research associate." Mostly plain prose, a job
              description you'd hand a new analyst.</p>
          </Card>
          <SkillCard />
        </div>
      </FieldNoteRow>
    </section>
  );
}

// ---- Need section
function Need() {
  return (
    <section id="need">
      <FieldNoteRow label="before we begin" hint="two things to set up first">
        <h2>Before we begin</h2>
        <p>The agent we'll download is a <b>Claude Code subagent</b>, a specialized
          assistant that Claude Code loads from a folder and delegates work to. So
          before we can leverage it, we need two things in place: the program that runs it,
          and the folder that defines it.</p>
        <p>First, <b>Claude Code</b> itself, Anthropic's command-line coding agent. It's
          the program that reads the agent definition and does the work. If you don't have it
          yet, start here:</p>
        <div className="callout">
          <h3>1 · Install Claude Code</h3>
          <p>Read the overview and follow the install steps at
            <a href="https://code.claude.com/docs/en/overview" target="_blank" rel="noopener"> code.claude.com/docs/en/overview</a>.
            Once <code>claude</code> runs in your terminal, come back here.</p>
        </div>
        <div className="callout" style={{marginTop: '14px', borderLeftColor: 'var(--terra)'}}>
          <h3>2 · Download this folder</h3>
          <p>This folder <em>is</em> the subagent, the agent definition, its skills, and the
            input/output trays. Download it, unzip it, and open it in Finder; the rest of this
            guide walks you through it.</p>
          <p style={{marginTop: '14px'}}>
            <a className="dlbtn" href="https://github.com/omars-lab/getting-started-with-claude-agents/releases/latest/download/getting-started-with-claude-agents.zip">↓ Download the folder (.zip)</a>
          </p>
        </div>
      </FieldNoteRow>
    </section>
  );
}

// ---- FinderShot: a figure with a screenshot.
function FinderShot({src, alt, caption, figStyle, imgStyle}) {
  return (
    <figure style={figStyle}>
      <img className="shot" alt={alt} src={src} style={imgStyle} />
      <figcaption>{caption}</figcaption>
    </figure>
  );
}

// ---- Open section
function Open() {
  return (
    <section id="open">
      <FieldNoteRow label="look first" hint="get into the folder">
        <h2>Open the folder</h2>
        <p>In Finder, the unzipped folder (<code>getting-started-with-claude-agents</code>)
          looks ordinary at first, a readme and the input/output trays. The interesting
          part is hidden.</p>
        <FinderShot
          src={finderHidden}
          alt="Finder window showing the downloaded folder with agent-inputs, agent-outputs, and README. The .claude folder is hidden."
          caption={<Fragment><b>The folder as you first see it.</b> Notice there's no
            <code> .claude</code> yet, macOS hides anything that starts with a dot.
            You'll launch the agent from here in a moment, first, a look at what's inside.</Fragment>} />
      </FieldNoteRow>
    </section>
  );
}

// ---- Reveal section
function Reveal() {
  return (
    <section id="reveal">
      <FieldNoteRow label="look first" hint="see what's really in here">
        <h2>Reveal the hidden <code>.claude</code> folder</h2>
        <p>The agent and its skills live in a folder named <code>.claude</code>.
          The leading dot keeps it out of the way during normal use, but you want
          to see it. In any Finder window, press:</p>
        <p style={{fontSize: '22px', margin: '6px 0 22px'}}>
          <kbd>⌘</kbd>  <kbd>⇧</kbd>  <kbd>.</kbd>
          <span style={{fontSize: '15px', color: 'var(--dim)', fontFamily: 'var(--mono)'}}> Command + Shift + Period</span>
        </p>
        <p>Hidden files fade into view. Press it again any time to hide them.</p>
        <FinderShot
          figStyle={{marginTop: '18px'}}
          src={finderShown}
          alt="The same Finder window after pressing Command Shift Period. Now .claude and .venv appear, dimmed, with .claude selected."
          caption={<Fragment><b>After the shortcut.</b> <code>.claude</code> and
            <code> .venv</code> appear (dimmed, because they're hidden by default).
            <code> .claude</code> is the one that matters, open it next.</Fragment>} />
      </FieldNoteRow>
    </section>
  );
}

// ---- AnatomyTabs: the .anatomy tabbed panel.
function AnatomyTabs() {
  const [tab, setTab] = useState('agents');
  const [skill, setSkill] = useState(null);
  const skillNames = Object.keys(SKILLS);

  const tabs = [
    {id: 'agents', ico: '📁', label: 'agents/'},
    {id: 'skills', ico: '📁', label: 'skills/'},
    {id: 'plans', ico: '📁', label: 'plans/'},
    {id: 'settings', ico: '📄', label: 'settings.json'},
  ];

  return (
    <div className="anatomy">
      <div className="tree" role="tablist" aria-label="Contents of .claude">
        {tabs.map(t => (
          <button key={t.id} role="tab" aria-selected={tab === t.id ? 'true' : 'false'}
            data-panel={t.id} onClick={() => setTab(t.id)}>
            <span className="ico">{t.ico}</span>{t.label}
          </button>
        ))}
      </div>
      <div className="detail">
        <div className={'panel' + (tab === 'agents' ? ' on' : '')} id="agents" role="tabpanel">
          <h3>agents/ : the role</h3>
          <div className="path">{'.claude/agents/<name>.md'}</div>
          <p>One Markdown file per agent. Here there's exactly one, the role this
            whole folder is built around:</p>
          <div className="chips">
            <button className="chip sel" data-agent="stock-analyzer">📄 stock-analyzer.md</button>
          </div>
          <div className="skilldesc">
            <b>stock-analyzer.md</b> <span className="role">the agent definition</span><br/>
            The file that <em>is</em> the agent: who it is, the workflow it follows, the
            guardrails it won't cross, and the skills it can call. Read it like an
            analyst's job description. The first two lines, <code>name</code> and
            <code> description</code>, are all Claude needs to know when to use it;
            everything below is the playbook.
          </div>
        </div>
        <div className={'panel' + (tab === 'skills' ? ' on' : '')} id="skills" role="tabpanel">
          <h3>skills/ : the recipes</h3>
          <div className="path">{'.claude/skills/<name>/SKILL.md'}</div>
          <p>One folder per skill, each a self-contained recipe the agent follows.
            Every <code>SKILL.md</code> has the same shape: a description, the output
            it owns, numbered steps, the standards that make it trustworthy, and the
            mistakes to avoid. <b>Click a skill</b> to see what it does:</p>
          <div className="chips" id="skillchips">
            {skillNames.map(name => (
              <button key={name} className={'chip' + (skill === name ? ' sel' : '')}
                data-skill={name} onClick={() => setSkill(name)}>{name}</button>
            ))}
          </div>
          <div className="skilldesc" id="skilldesc" aria-live="polite">
            {skill
              ? <Fragment><b>{skill}</b> <span className="role">{': ' + SKILLS[skill][0]}</span><br/>{SKILLS[skill][1]}</Fragment>
              : <span className="hint">↑ Pick a skill to read its one-line job.</span>}
          </div>
        </div>
        <div className={'panel' + (tab === 'plans' ? ' on' : '')} id="plans" role="tabpanel">
          <h3>plans/ : how it got built</h3>
          <div className="path">.claude/plans/</div>
          <p>Notes-to-self the agent wrote while planning bigger changes, here,
            the refactor that turned this into the Stock Analyzer. Not required to
            run anything; it's the paper trail, useful when you want to understand
            <em> why</em> the folder looks the way it does.</p>
        </div>
        <div className={'panel' + (tab === 'settings' ? ' on' : '')} id="settings" role="tabpanel">
          <h3>settings.json : the permissions</h3>
          <div className="path">.claude/settings.json</div>
          <p>The rules of engagement: which commands and web domains the agent may
            touch (<code>allow</code>) and which it must never (<code>deny</code>,
            e.g. reading <code>.env</code> secrets or deleting files). This is how
            you keep an autonomous agent on a short, explicit leash.</p>
        </div>
      </div>
    </div>
  );
}

// ---- Anatomy section
function Anatomy() {
  return (
    <section id="anatomy">
      <FieldNoteRow label="look first" hint="read the four things inside">
        <h2>Inside <code>.claude</code></h2>
        <p>Four things. Click each to see what it's for, this is the entire anatomy
          of the agent.</p>
        <FinderShot
          figStyle={{margin: '6px 0 26px'}}
          src={finderClaude}
          alt="Finder window showing the contents of the .claude folder: agents, skills, plans folders and a settings.json file."
          caption={<Fragment><b>The contents of <code>.claude</code>.</b> Three folders and one settings file.</Fragment>} />
        <AnatomyTabs />
      </FieldNoteRow>
    </section>
  );
}

// ---- Steps: the .steps ordered list wrapper.
function Steps({children}) {
  return <ol className="steps">{children}</ol>;
}

// ---- ShortlistMockup: a static <Mockup> from @omars-lab/blog-ui showing the checkpoint the
// agent pauses on. The reader-facing "agent in motion" beat is the terminal GIF below it; the
// scripted <Walkthrough> was removed as redundant. This frame stays for the picture of the
// checkpoint AND as the cross-repo proof that the package installs + renders in a real second
// repo (the point of the "shipping a component package" writeup).
function ShortlistMockup() {
  return (
    <figure style={{margin: '22px 0 4px'}}>
      <Mockup chrome="terminal" title="stock-analyzer" url="">
        <p style={{margin: '0 0 10px'}}>Catalyst sweep found these worth a closer look today:</p>
        <ul style={{margin: '0 0 14px', paddingLeft: '20px', lineHeight: 1.8}}>
          <li>NVDA: unusual options volume + analyst upgrade</li>
          <li>CRWD: earnings tomorrow, elevated IV</li>
          <li>SMCI: 8-K filed, insider Form 4 buys</li>
        </ul>
        <button style={{font: 'inherit', padding: '8px 16px', borderRadius: '8px',
          border: 'none', background: '#D97757', color: '#fff', cursor: 'pointer'}}>
          Approve &amp; run full analysis
        </button>
      </Mockup>
      <figcaption><b>The checkpoint.</b> It proposes a shortlist and stops, analysis time
        is the costly step, so it confirms before spending it. (Rendered by the
        <code> @omars-lab/blog-ui</code> package.)</figcaption>
    </figure>
  );
}

// ---- Run section
function Run() {
  return (
    <section id="run">
      <FieldNoteRow label="getting started" hint="four steps, start to finish">
        <h2>Getting started</h2>
        <p>You've seen what's in the folder. Now run it.</p>

        <Steps>
          <li>
            <h3>Open the Terminal app</h3>
            <p>Press <kbd>⌘</kbd> <kbd>Space</kbd> to open <b>Spotlight</b>, type
              <code> terminal</code>, and press <kbd>Return</kbd> to launch the Terminal app.</p>
            <FinderShot
              figStyle={{margin: '14px 0 4px'}}
              src={spotlight}
              alt="macOS Spotlight search open with 'terminal' typed and Terminal.app as the top result."
              caption={<Fragment><b>⌘ Space, then type "terminal."</b> Terminal is where you talk to
                Claude Code.</Fragment>} />
          </li>
          <li>
            <h3>Point Terminal at this folder and start Claude</h3>
            <p>Type <code>cd </code> (with a trailing space), then <b>drag the unzipped
              folder from Finder onto the Terminal window</b>, it fills in the path. Press
              <kbd>Return</kbd>, then run <code>claude</code>:</p>
            <pre className="term"><span className="p">$</span> cd <span className="dim">~/Downloads/getting-started-with-claude-agents</span>{'\n'}<span className="p">$</span> claude</pre>
            <p style={{fontSize: '14px', color: 'var(--ink-soft)', marginTop: '10px'}}>First time in a
              new folder, Claude Code asks you to trust it, say yes. Then you're in a session.</p>
          </li>
          <li>
            <h3>Wait for Claude to start</h3>
            <p>A terminal window opens and Claude Code boots up. When it's ready you'll
              see the welcome splash and an empty input box with a <code>›</code> prompt,
              that's Claude waiting for your first message.</p>
            <FinderShot
              figStyle={{margin: '14px 0 4px'}}
              src={claudeSplash}
              alt="The Claude Code startup splash: a pixel mascot, 'Claude Code v2.1.183', 'Opus 4.8 with high effort', the working directory, and an empty input box with a cursor, waiting for input."
              caption={<Fragment><b>Claude is ready.</b> The empty <code>›</code> box means it's
                waiting for you. The status line shows the model and folder you're in.</Fragment>} />
          </li>
          <li>
            <h3>Type <code>/agents</code> to confirm the agent is there</h3>
            <p>Claude Code reads the <code>.claude/agents/</code> folder automatically.
              Type <code>/agents</code> and you'll see <code>stock-analyzer</code> listed
              as a <b>Project agent</b>, already configured, nothing to install.</p>
            <FinderShot
              figStyle={{margin: '14px 0 4px'}}
              src={claudeAgents}
              alt="The Claude Code /agents Library panel showing stock-analyzer registered as a Project agent loaded from .claude/agents, with model set to inherit."
              caption={<Fragment><b><code>/agents</code> → Library.</b> Picked up from
                <code> .claude/agents</code> with no extra setup. <code>inherit</code> means
                it uses whatever model your session is on.</Fragment>} />
          </li>
          <li>
            <h3>Ask it the question</h3>
            <p>Ask plainly: <em>"what stocks are worth considering today?"</em> It sweeps
              for catalysts, proposes a shortlist, and, importantly, <b>stops to let you
              approve</b> before doing the expensive work. Then it fans out: data,
              analysis, a workbook, and a stress test per name.</p>
            <ShortlistMockup />
            <FinderShot
              figStyle={{margin: '14px 0 4px'}}
              imgStyle={{background: '#FBF4E4'}}
              src={terminalGif}
              alt="Animated Claude Code session: the prompt 'what stocks are worth considering today', Claude launching the stock-analyzer agent, the subagent running tool calls, and a shortlist of names."
              caption={<Fragment><b>A real session.</b> Claude launches the
                <code> stock-analyzer</code> agent, which runs its skills and tools, then
                pauses at the shortlist, analysis time is the costly step, so it confirms
                before spending it.</Fragment>} />
          </li>
        </Steps>
      </FieldNoteRow>
    </section>
  );
}

// ---- IO section
function IO() {
  return (
    <section id="io">
      <FieldNoteRow label="convention" hint="where files go in and come out">
        <h2>Giving it files, getting files back</h2>
        <p>To keep things obvious, the agent has been configured to use two
          plainly-named folders, one for what you give it, one for what it produces.
          You don't need to remember internal paths; just drop and collect.</p>
        <div className="io">
          <div className="box in">
            <span className="tag">You give it →</span>
            <h3 style={{margin: '8px 0 4px'}}>agent-inputs/</h3>
            <p style={{fontSize: '15px', margin: 0, color: 'var(--ink-soft)'}}>Anything you want
              the agent to work from, a watchlist, a ticker list, a thesis to
              pressure-test. There's an example <code>watchlist.md</code> in there
              already; edit it or drop your own.</p>
            <code>./agent-inputs/watchlist.md</code>
          </div>
          <div className="arrow">→</div>
          <div className="box out">
            <span className="tag">→ It gives back</span>
            <h3 style={{margin: '8px 0 4px'}}>agent-outputs/</h3>
            <p style={{fontSize: '15px', margin: 0, color: 'var(--ink-soft)'}}>Everything it
              produces, reports, workbooks, the per-ticker data cache. Collect it here.</p>
            <code>./agent-outputs/</code>
          </div>
        </div>
      </FieldNoteRow>
    </section>
  );
}

// ---- Next section
function Next() {
  return (
    <section id="next">
      <FieldNoteRow label="now you" hint="the point is to change it">
        <h2>Make it yours</h2>
        <p>The structure is the lesson. Now bend it:</p>
        <Steps>
          <li><h3>Read three files</h3><p>The agent (<code>stock-analyzer.md</code>),
            the cleanest skill (<code>xlsx-author</code>), and the most opinionated one
            (<code>thesis-stress-test</code>). That's the whole pattern.</p>
            <FinderShot
              figStyle={{margin: '12px 0 4px'}}
              src={finderAgents}
              alt="Finder window inside .claude/agents showing the single file stock-analyzer.md, labeled 'the role, read this first'."
              caption={<Fragment><b><code>.claude/agents/</code></b>, one file, the role. Open it
                in any text editor; it's plain Markdown.</Fragment>} />
          </li>
          <li><h3>Add a skill</h3><p>Copy any <code>SKILL.md</code>, change the recipe,
            point the agent at it. No framework, no registry, just Markdown.</p>
            <FinderShot
              figStyle={{margin: '12px 0 4px'}}
              src={finderSkills}
              alt="Finder window inside .claude/skills showing skill folders like xlsx-author (labeled 'copy this one') and thesis-stress-test."
              caption={<Fragment><b><code>.claude/skills/</code></b>, one folder per skill. Duplicate
                <code> xlsx-author/</code>, rename it, rewrite its <code>SKILL.md</code>, and
                the agent can call it.</Fragment>} />
          </li>
          <li><h3>Tighten a rule</h3><p>Edit a skill's <em>Standards</em> section, or the
            <code> deny</code> list in <code>settings.json</code>. The agent picks it up next run.</p></li>
        </Steps>
        <p style={{marginTop: '24px'}}>Read the <a href="README.md">README</a> for the full
          tour, the setup steps, and the file map.</p>
      </FieldNoteRow>
    </section>
  );
}

// ---- DeployPaths: the three deploy path cards.
function DeployPaths() {
  return (
    <div className="paths">
      <a className="pathcard here" href="https://code.claude.com/docs/en/sub-agents" target="_blank" rel="noopener">
        <span className="ptag">You are here</span>
        <h3>Interactive · Sub-agents</h3>
        <p>Run it in a Claude Code session as a sub-agent. Best for hands-on use,
          iteration, and learning, with you approving each checkpoint.</p>
        <span className="plink">code.claude.com/docs/en/sub-agents ↗</span>
      </a>
      <a className="pathcard" href="https://platform.claude.com/docs/en/managed-agents/overview" target="_blank" rel="noopener">
        <span className="ptag">Deploy · Hosted</span>
        <h3>Managed Agents</h3>
        <p>Hand the agent to Anthropic's hosted runtime so it can run on its own,
          no infrastructure to operate. Good when you want a deployed service, not
          a local session.</p>
        <span className="plink">platform.claude.com · managed-agents ↗</span>
      </a>
      <a className="pathcard" href="https://code.claude.com/docs/en/agent-sdk/overview" target="_blank" rel="noopener">
        <span className="ptag">Deploy · Code</span>
        <h3>Agent SDK</h3>
        <p>Lift the agent and its skills into your own environment and drive them
          programmatically, schedule runs (a cron, a queue), wire in triggers, and
          run fully automated.</p>
        <span className="plink">code.claude.com · agent-sdk ↗</span>
      </a>
    </div>
  );
}

// ---- Deploy section
function Deploy() {
  return (
    <section id="deploy">
      <FieldNoteRow label="going further" hint="where this can run">
        <h2>Where this runs, and how to deploy it</h2>
        <p>What you've been using is an <b>interactive Claude Code session</b>: you
          type, the agent works, it stops at checkpoints for your approval. That's
          what this folder is built for, and it's the right mode while you're
          learning, iterating, or doing real research alongside it.</p>
        <p>The agent itself is just Markdown, a definition plus its skills. That
          portability is the point: when you want it to run <em>without</em> you in
          the loop, on a schedule, triggered by an event, as a service, you lift
          the same files into a runtime built for that. Two paths:</p>

        <DeployPaths />
        <p style={{marginTop: '22px', color: 'var(--ink-soft)'}}>The skills don't change
          between modes. A skill that knows how to pull filings and build a workbook
          does the same job whether you invoked it by hand or a scheduler did. That's
          the payoff of keeping the <em>who</em> and the <em>how</em> as plain files.</p>
      </FieldNoteRow>
    </section>
  );
}

// ---- Egress section
function Egress() {
  return (
    <section id="egress">
      <FieldNoteRow label="thanks" hint="one more thing">
        <h2>Enjoyed this?</h2>
        <p>If this walkthrough was useful, I write more about agents, engineering, and
          building things at my blog:</p>
        <p style={{marginTop: '14px'}}>
          <a className="dlbtn" href="https://blog.bytesofpurpose.com/thoughts" target="_blank" rel="noopener">Read more on Bytes of Purpose →</a>
        </p>
      </FieldNoteRow>
    </section>
  );
}

// ---- App: composes everything in order.
export default function App() {
  return (
    <Fragment>
      <Hero />
      <BigIdea />
      <Need />
      <Open />
      <Reveal />
      <Anatomy />
      <Run />
      <IO />
      <Next />
      <Deploy />
      <Egress />
      <footer>
        <div className="wrap">
          Stock Analyzer: a teaching example for Claude Code agents.
          · Built with Vite + React; the live demo is rendered by the @omars-lab/blog-ui package.
        </div>
      </footer>
    </Fragment>
  );
}
