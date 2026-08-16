# CS 499 Computer Science Capstone ePortfolio

This repository contains Bruno Manuel's final SNHU CS 499 ePortfolio, including:

- professional self-assessment presented on the home page;
- [informal code review](https://vimeo.com/1218736228);
- original and enhanced artifacts for Software Design and Engineering;
- original and enhanced artifacts for Algorithms and Data Structures;
- original and enhanced artifacts for Databases;
- downloadable milestone narratives; and
- explicit evidence for all five Computer Science program outcomes.

## Verification

The enhanced network-automation database artifact passes 16 automated tests:

```bash
cd artifacts/databases/enhanced
python3 -m unittest discover -s tests -v
```

The Appointment Service uses Java 17, Maven, and JUnit 5:

```bash
cd artifacts/software-engineering/enhanced
mvn test
```

## Portfolio

After GitHub Pages deployment, the project site is available at:

<https://dos2164bmt.github.io/CS499_Portfolio/>
