/**
 * QuizInterface - Interactive quiz component for chapter assessments
 */
import React, { useEffect } from 'react';
import { useQuiz, QuizStatus } from '../../hooks/useQuiz';
import {
  Play,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  Loader2,
  RotateCcw,
  Clock,
  Award,
} from 'lucide-react';
import styles from './styles.module.css';

/**
 * Format time in mm:ss
 */
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Question component
 */
function Question({ question, selectedAnswer, onAnswer }) {
  const isMultipleChoice = question.question_type === 'multiple_choice';
  const isTrueFalse = question.question_type === 'true_false';
  const isCodeCompletion = question.question_type === 'code_completion';

  const options = isTrueFalse
    ? ['True', 'False']
    : question.options || [];

  return (
    <div className={styles.question}>
      <div className={styles.questionHeader}>
        <span className={styles.difficulty}>{question.difficulty}</span>
        <span className={styles.points}>{question.points} pts</span>
      </div>

      <p className={styles.questionText}>{question.question_text}</p>

      {/* Multiple choice / True-False options */}
      {(isMultipleChoice || isTrueFalse) && (
        <div className={styles.options}>
          {options.map((option, index) => (
            <button
              key={index}
              className={`${styles.option} ${selectedAnswer === option ? styles.selected : ''}`}
              onClick={() => onAnswer(option)}
            >
              <span className={styles.optionLabel}>
                {String.fromCharCode(65 + index)}
              </span>
              <span className={styles.optionText}>{option}</span>
            </button>
          ))}
        </div>
      )}

      {/* Code completion input */}
      {isCodeCompletion && (
        <div className={styles.codeInput}>
          <textarea
            value={selectedAnswer || ''}
            onChange={(e) => onAnswer(e.target.value)}
            placeholder="Enter your code answer..."
            className={styles.codeTextarea}
            rows={4}
          />
        </div>
      )}
    </div>
  );
}

/**
 * Results component
 */
function Results({ results, quiz, onRetry }) {
  const passed = results.passed;
  const percentage = results.score;

  return (
    <div className={styles.results}>
      <div className={`${styles.resultHeader} ${passed ? styles.passed : styles.failed}`}>
        {passed ? (
          <Award size={48} className={styles.resultIcon} />
        ) : (
          <XCircle size={48} className={styles.resultIcon} />
        )}
        <h2>{passed ? 'Congratulations!' : 'Keep Learning'}</h2>
        <p>
          {passed
            ? 'You passed the quiz!'
            : `You need ${quiz.passing_score}% to pass. Try again!`}
        </p>
      </div>

      <div className={styles.scoreCard}>
        <div className={styles.scoreStat}>
          <span className={styles.scoreValue}>{percentage.toFixed(1)}%</span>
          <span className={styles.scoreLabel}>Score</span>
        </div>
        <div className={styles.scoreStat}>
          <span className={styles.scoreValue}>
            {results.points_earned}/{results.total_points}
          </span>
          <span className={styles.scoreLabel}>Points</span>
        </div>
      </div>

      <div className={styles.resultsList}>
        <h3>Question Results</h3>
        {results.results.map((result, index) => (
          <div
            key={result.question_id}
            className={`${styles.resultItem} ${result.is_correct ? styles.correct : styles.incorrect}`}
          >
            <div className={styles.resultItemHeader}>
              {result.is_correct ? (
                <CheckCircle size={20} className={styles.correctIcon} />
              ) : (
                <XCircle size={20} className={styles.incorrectIcon} />
              )}
              <span>Question {index + 1}</span>
              <span className={styles.resultPoints}>
                {result.points_awarded} pts
              </span>
            </div>

            <p className={styles.resultQuestion}>{result.question_text}</p>

            <div className={styles.answerComparison}>
              <div className={styles.userAnswer}>
                <span className={styles.answerLabel}>Your answer:</span>
                <span>{result.user_answer || '(No answer)'}</span>
              </div>
              {!result.is_correct && (
                <div className={styles.correctAnswer}>
                  <span className={styles.answerLabel}>Correct answer:</span>
                  <span>{result.correct_answer}</span>
                </div>
              )}
            </div>

            {result.explanation && (
              <div className={styles.explanation}>
                <span className={styles.explanationLabel}>Explanation:</span>
                <p>{result.explanation}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <button className={styles.retryButton} onClick={onRetry}>
        <RotateCcw size={18} />
        Try Again
      </button>
    </div>
  );
}

/**
 * Main QuizInterface component
 */
export default function QuizInterface({ chapterId }) {
  const {
    status,
    quiz,
    questions,
    currentQuestion,
    currentIndex,
    answers,
    results,
    error,
    progress,
    elapsedTime,
    loadQuiz,
    startQuiz,
    answerQuestion,
    nextQuestion,
    prevQuestion,
    goToQuestion,
    submitQuiz,
    resetQuiz,
  } = useQuiz(chapterId);

  // Load quiz on mount
  useEffect(() => {
    if (status === QuizStatus.IDLE && chapterId) {
      loadQuiz();
    }
  }, [status, loadQuiz, chapterId]);

  // No chapter ID provided
  if (!chapterId) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <XCircle size={32} />
          <p>No chapter specified for quiz.</p>
        </div>
      </div>
    );
  }

  // Loading state
  if (status === QuizStatus.LOADING) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <Loader2 size={32} className={styles.spinner} />
          <p>Loading quiz...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (status === QuizStatus.ERROR) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <XCircle size={32} />
          <p>{error}</p>
          <button onClick={loadQuiz} className={styles.retryButton}>
            <RotateCcw size={18} />
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Ready state (quiz loaded but not started)
  if (status === QuizStatus.READY && quiz) {
    return (
      <div className={styles.container}>
        <div className={styles.startScreen}>
          <h2>{quiz.title}</h2>
          {quiz.instructions && <p className={styles.instructions}>{quiz.instructions}</p>}
          <div className={styles.quizMeta}>
            <span>{quiz.questions.length} Questions</span>
            <span>Passing Score: {quiz.passing_score}%</span>
          </div>
          <button className={styles.startButton} onClick={startQuiz}>
            <Play size={20} />
            Start Quiz
          </button>
        </div>
      </div>
    );
  }

  // Completed state (show results)
  if (status === QuizStatus.COMPLETED && results) {
    return (
      <div className={styles.container}>
        <Results results={results} quiz={quiz} onRetry={resetQuiz} />
      </div>
    );
  }

  // Submitting state
  if (status === QuizStatus.SUBMITTING) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <Loader2 size={32} className={styles.spinner} />
          <p>Submitting your answers...</p>
        </div>
      </div>
    );
  }

  // In progress state
  if (status === QuizStatus.IN_PROGRESS && currentQuestion) {
    const isLastQuestion = currentIndex === progress.total - 1;
    const hasCurrentAnswer = answers[currentQuestion.id] !== undefined;

    return (
      <div className={styles.container}>
        {/* Header with timer and progress */}
        <div className={styles.header}>
          <div className={styles.timer}>
            <Clock size={16} />
            <span>{formatTime(elapsedTime)}</span>
          </div>
          <div className={styles.progressText}>
            Question {progress.current} of {progress.total}
          </div>
        </div>

        {/* Progress bar */}
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progress.percentage}%` }}
          />
        </div>

        {/* Question dots */}
        <div className={styles.questionDots}>
          {questions.map((q, index) => (
            <button
              key={q.id}
              className={`${styles.dot} ${index === currentIndex ? styles.current : ''} ${answers[q.id] !== undefined ? styles.answered : ''}`}
              onClick={() => goToQuestion(index)}
              title={`Question ${index + 1}`}
            />
          ))}
        </div>

        {/* Current question */}
        <Question
          question={currentQuestion}
          selectedAnswer={answers[currentQuestion.id]}
          onAnswer={answerQuestion}
        />

        {/* Navigation */}
        <div className={styles.navigation}>
          <button
            className={styles.navButton}
            onClick={prevQuestion}
            disabled={currentIndex === 0}
          >
            <ChevronLeft size={20} />
            Previous
          </button>

          {isLastQuestion ? (
            <button
              className={`${styles.navButton} ${styles.submitButton}`}
              onClick={submitQuiz}
              disabled={!progress.isComplete}
            >
              Submit Quiz
              <CheckCircle size={20} />
            </button>
          ) : (
            <button
              className={styles.navButton}
              onClick={nextQuestion}
            >
              Next
              <ChevronRight size={20} />
            </button>
          )}
        </div>

        {/* Answered count */}
        <div className={styles.answeredCount}>
          {progress.answeredCount} of {progress.total} answered
        </div>
      </div>
    );
  }

  return null;
}
