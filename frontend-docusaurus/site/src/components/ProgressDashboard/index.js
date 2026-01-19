/**
 * ProgressDashboard - Shows overall learning progress
 */
import React, { useEffect } from 'react';
import Link from '@docusaurus/Link';
import {
  BookOpen,
  CheckCircle,
  Clock,
  Award,
  TrendingUp,
  Bookmark,
  Loader2,
} from 'lucide-react';
import { useProgress } from '../../hooks/useProgress';
import styles from './styles.module.css';

/**
 * Progress circle component
 */
function ProgressCircle({ percentage, size = 120, strokeWidth = 8 }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg width={size} height={size} className={styles.progressCircle}>
      {/* Background circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--ifm-color-emphasis-200)"
        strokeWidth={strokeWidth}
      />
      {/* Progress circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--ifm-color-primary)"
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        className={styles.progressArc}
      />
      {/* Percentage text */}
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dy="0.35em"
        className={styles.progressText}
      >
        {Math.round(percentage)}%
      </text>
    </svg>
  );
}

/**
 * Stat card component
 */
function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className={styles.statCard}>
      <div className={styles.statIcon} style={{ color }}>
        <Icon size={24} />
      </div>
      <div className={styles.statInfo}>
        <span className={styles.statValue}>{value}</span>
        <span className={styles.statLabel}>{label}</span>
      </div>
    </div>
  );
}

/**
 * Main ProgressDashboard component
 */
export default function ProgressDashboard() {
  const {
    overallProgress,
    bookmarks,
    isLoading,
    error,
    fetchProgress,
  } = useProgress();

  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <Loader2 className={styles.spinner} size={32} />
        <span>Loading progress...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.error}>
        <p>Unable to load progress. Please sign in to track your learning.</p>
      </div>
    );
  }

  if (!overallProgress) {
    return (
      <div className={styles.noProgress}>
        <BookOpen size={48} className={styles.emptyIcon} />
        <h3>Start Your Learning Journey</h3>
        <p>Begin reading chapters to track your progress.</p>
        <Link
          to="/docs/module-01/chapter-01-introduction"
          className={styles.startButton}
        >
          Start Learning
        </Link>
      </div>
    );
  }

  const {
    total_chapters = 13,
    completed_chapters = 0,
    total_quizzes_taken = 0,
    average_quiz_score = 0,
    total_time_spent_minutes = 0,
  } = overallProgress;

  const completionPercentage = (completed_chapters / total_chapters) * 100;

  return (
    <div className={styles.dashboard}>
      <h2 className={styles.title}>Your Learning Progress</h2>

      <div className={styles.mainProgress}>
        <ProgressCircle percentage={completionPercentage} size={150} />
        <div className={styles.progressDetails}>
          <h3>Course Completion</h3>
          <p>
            {completed_chapters} of {total_chapters} chapters completed
          </p>
        </div>
      </div>

      <div className={styles.stats}>
        <StatCard
          icon={CheckCircle}
          label="Chapters Completed"
          value={completed_chapters}
          color="var(--ifm-color-success)"
        />
        <StatCard
          icon={Award}
          label="Quizzes Taken"
          value={total_quizzes_taken}
          color="var(--ifm-color-primary)"
        />
        <StatCard
          icon={TrendingUp}
          label="Avg. Quiz Score"
          value={`${Math.round(average_quiz_score)}%`}
          color="var(--ifm-color-warning)"
        />
        <StatCard
          icon={Clock}
          label="Time Spent"
          value={`${Math.round(total_time_spent_minutes / 60)}h`}
          color="var(--ifm-color-info)"
        />
      </div>

      {/* Bookmarks Section */}
      {bookmarks && bookmarks.length > 0 && (
        <div className={styles.bookmarksSection}>
          <h3>
            <Bookmark size={20} />
            Your Bookmarks
          </h3>
          <div className={styles.bookmarksList}>
            {bookmarks.map((bookmark) => (
              <Link
                key={bookmark.chapter_id}
                to={`/docs/${bookmark.module_id}/${bookmark.chapter_id}`}
                className={styles.bookmarkItem}
              >
                <span className={styles.bookmarkTitle}>{bookmark.title}</span>
                <span className={styles.bookmarkModule}>{bookmark.module}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Continue Learning */}
      <div className={styles.continueSection}>
        <h3>Continue Learning</h3>
        <Link
          to="/docs/module-01/chapter-01-introduction"
          className={styles.continueButton}
        >
          <BookOpen size={20} />
          Resume Course
        </Link>
      </div>
    </div>
  );
}
