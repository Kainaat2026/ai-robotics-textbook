import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'ROS 2 & Robot Programming',
    emoji: '🤖',
    description: (
      <>
        Master ROS 2, the industry-standard framework for robotics. Learn nodes,
        topics, services, and actions to build modular robot software.
      </>
    ),
  },
  {
    title: 'AI-Powered Simulation',
    emoji: '🎮',
    description: (
      <>
        Train and test robots in Gazebo, Unity, and NVIDIA Isaac Sim.
        Learn sim-to-real transfer to deploy trained models to physical robots.
      </>
    ),
  },
  {
    title: 'Vision-Language-Action Models',
    emoji: '🧠',
    description: (
      <>
        Explore cutting-edge VLA models that combine vision, language understanding,
        and robot control for intelligent humanoid systems.
      </>
    ),
  },
];

function Feature({emoji, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center" style={{fontSize: '4rem', marginBottom: '1rem'}}>
        {emoji}
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
