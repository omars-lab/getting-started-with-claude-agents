// Proof-of-consumption scaffold: imports @omars-lab/blog-ui (published to GitHub Packages)
// and its bundled stylesheet, then renders the components. If this builds and renders, the
// package is consumable by a real bundler in another repo. The richer demo content lands next.
import {Mockup, Walkthrough} from '@omars-lab/blog-ui';
import '@omars-lab/blog-ui/style.css';

export default function App() {
  return (
    <main style={{maxWidth: 820, margin: '0 auto', padding: '2rem 1rem'}}>
      <h1>Getting Started with Claude Agents</h1>
      <p>
        This page is built with Vite and React, and it consumes the
        <code> @omars-lab/blog-ui </code> component package straight from GitHub Packages.
      </p>

      <Walkthrough
        steps={[
          {type: 'scene', to: 'claude', say: 'Claude opens the agent for review',
            prompt: 'review the stock-analyzer agent',
            tools: [{verb: 'Open', target: 'stock-analyzer.md', note: 'the agent'},
                    {verb: 'Read', target: 'SKILL.md'}]},
          {type: 'scene', to: 'app', say: 'You review it in the browser'},
          {type: 'highlight', target: '#wt-role', say: 'the role'},
          {type: 'scene', to: 'claude', say: 'Claude continues on your feedback',
            prompt: 'continue',
            intro: 'Feedback received. Applying your changes now.',
            tools: [{verb: 'Update', target: 'stock-analyzer.md'},
                    {target: 'continued', done: true}]},
        ]}
      >
        <Mockup chrome="browser" title="Agent Review" url="agents.local/stock-analyzer">
          <p>
            <span id="wt-role">stock-analyzer</span> reads a watchlist and writes a report.
          </p>
        </Mockup>
      </Walkthrough>
    </main>
  );
}
