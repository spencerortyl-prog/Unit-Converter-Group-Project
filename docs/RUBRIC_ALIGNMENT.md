# Rubric alignment and submission checklist

## Scope

The requested deliverable is a Python unit converter with at least 400 lines, using
GitHub and the supplied grading documents. The documents also describe separate
presentation, report, and recording submissions. This project provides the program,
tests, and planning material; it is not a finished PowerPoint, formatted report, or recording.

## Code requirement

The main application contains 460 physical lines and 411 nonblank lines. Tests and
Markdown documentation are additional and are not needed to reach 400 physical lines.
Use the tokenizer-based count in verification.txt for a stricter code-only measure.
Do not represent AI-generated code as 400 lines independently written by your group.

| Required concept | Concrete use |
| --- | --- |
| Control loops | Menu loop, unit search, history display, batch rows |
| Strings | Prompts, symbols, names, error messages, formatted results |
| Integers | Menu indexes, precision, batch counters, exit codes |
| Floats | Measurement values, factors, offsets, converted results |
| Booleans | Running state, negative-value policy, remember flag |
| None | Optional command-line arguments and action lookup default |
| Lists | Session history, batch rows, search results |
| Tuples | Immutable category units, CSV fields, returned batch counts |
| Dictionaries | Category registry, menu dispatch, CSV rows |
| Sets | Required CSV header membership checks |
| Functions | Category construction, parser construction, main entry point |
| Exceptions | Custom ConversionError, numeric/file/CSV error recovery |
| Object-oriented design | Unit, Category, Record, Converter, ConsoleApp |

The documents say all topics learned should be covered; the complete course syllabus
was not supplied. These are the concepts explicitly listed in the supplied rubric,
plus common Python types used naturally by the application. Inheritance beyond a
custom exception and specialized types such as complex numbers are not demonstrated.

## Presentation plan

Follow the ordered plan in DEMO_GUIDE.md. Add your real name, class, and actual topic
motivation. Reserve about 10 minutes for an individual or two-person presentation
(about 5 minutes per member), plus about 2 minutes for Q&A. Practice aloud.

## Report plan

Use Times New Roman, 12 pt. Include title, group number/names, class and subject code;
contents; abstract; goal; software requirements; introduction; your reason for choosing
the topic; existing techniques and improvements; detailed procedure and flow diagram;
results and screenshots; challenges and solutions; conclusion; future improvements;
public GitHub link; source-code appendix; references.

Explain the shared-base algorithm and temperature offsets with numerical examples.
Report actual observed outputs and test results. Discuss float precision, session-only
history, and batch memory use. Add your own reflection and contribution record.

## Submission checks

- Create a public GitHub repository, upload source and documentation, and insert its
  verified URL at the end of the presentation and in the report.
- Keep the source public until grading is complete.
- Track real individual contributions in commits; do not fabricate past contributions.
- Make the PowerPoint and Times New Roman 12 pt report.
- Capture screenshots and a screen recording with your explanation as backups.
- Demonstrate success and failure paths, not just the happy path.
- Practice answering questions and staying within the presentation time.

The supplied rubric states a submission deadline of December 1, 2026 at 11:59 PM;
it does not specify a timezone. Confirm the deadline in the course system.
