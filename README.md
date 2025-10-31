# ICTNexus , A Microservice Based University Management System

**Course:** CS 4122 – Distributed Systems and Cloud Computing  
**Faculty:** ICT Faculty  
**Instructor:** Daniel Moune  
**Author:** [NZEKUI NZOUDJIO ALICE CRESSENCE](mailto:nzekuinzoudjio.alice@ictu.edu.cm)  
**Matricule:** ICTU20241151  
**GitHub Repository:** [Cloud-based Distributed System](https://github.com/AliceCressence/Cloud-based-distributed-system)  
**Date:** October 15, 2025  

---

##  Abstract

This project proposes the redesign of the university’s Learning Management System (LMS) infrastructure into a **unified, cloud-native distributed system**.  
Currently, multiple isolated Moodle instances (Academics, Finance, HR) cause **data silos**, operational inefficiencies, and manual data transfers.  

### Key Objectives
- Integrate all Moodle instances through a **central event-driven communication backbone**.  
- Refactor monolithic Moodle functions into **independent microservices** (Enrollment, Billing, Grades).  
- Deploy on **AWS, GCP, or Azure**, orchestrated by **Kubernetes**.  
- Use **RabbitMQ** for asynchronous inter-service communication following the **Saga pattern**.  
- Achieve measurable KPIs:  
  - 99.95% uptime  
  - <200ms API latency  
  - 80% reduction in manual data entry  

---

##  Table of Contents

1. [Introduction & Problem Statement](#introduction--problem-statement)
2. [Project Scope](#project-scope)
3. [Proposed Solution](#proposed-solution)
4. [System Design & Architecture](#system-design--architecture)
5. [Technology Stack](#technology-stack)
6. [Project Plan & Timeline](#project-plan--timeline)
7. [Implementation Strategy](#implementation-strategy)
8. [Evaluation & Success Metrics](#evaluation--success-metrics)
9. [Conclusion](#conclusion)

---

## 1️ Introduction & Problem Statement

Universities face digital fragmentation due to isolated systems for Academics, Finance, and HR.  
Manual data exchange leads to inefficiencies, data loss, and poor user experience.

### Impact
- **Students:** Frustration due to delays and errors in course access or billing.  
- **Faculty:** No unified view of student status.  
- **Administrators:** Time wasted on redundant manual tasks.

### Strategic Implication
Data fragmentation blocks the university from leveraging real-time analytics for strategic decisions.

---

## 2️⃣ Project Scope

### In-Scope
- Integration of **three Moodle instances** (Academics, Finance, HR).  
- Development of an **event-driven central communication backbone**.  
- Deployment on **cloud-native infrastructure**.  
- **API refactoring** of Moodle monolith functions.

### Out-of-Scope
- Creation of new Moodle user-facing features.  
- Large-scale legacy data migration.  
- Complete Moodle replacement.

---

## 3️⃣ Proposed Solution

A **distributed microservices architecture** will provide scalability, fault tolerance, and organizational agility.

### Key Design Principles
- **Scalability:** Use Kubernetes Horizontal Pod Autoscaler.  
- **Resilience:** Implement PostgreSQL multi-AZ setup & Circuit Breaker pattern.  
- **Agility:** Enable asynchronous communication using **RabbitMQ** events.

---

## 4️⃣ System Design & Architecture

### Microservices Model
- **Authentication Service** – JWT-based user management  
- **Course Management Service** – Courses & rosters  
- **Enrollment Service** – Student enrollment orchestration  
- **Billing Service** – Invoice generation & payment processing  
- **Grades Service** – Grade management  
- **Notification Service** – Email/SMS/Push alerts  

### Communication
- **Asynchronous:** via RabbitMQ (publish-subscribe)  
- **Synchronous (exception):** via REST + Service Mesh (Istio/Linkerd)

### Data Consistency
- Each service maintains its own PostgreSQL DB.  
- Cross-service consistency ensured with the **Saga Pattern**.

---

## 5️⃣ Technology Stack

| Category | Technology | Description |
|-----------|-------------|-------------|
| **Language/Framework** | Python (FastAPI) | Modern async APIs with OpenAPI support |
| **Database** | PostgreSQL | ACID-compliant, JSONB support |
| **Messaging** | RabbitMQ | AMQP-based message broker |
| **Containerization** | Docker | Immutable, portable environments |
| **Orchestration** | Kubernetes | Automated deployment & scaling |
| **API Gateway** | Kong | Centralized routing, auth, rate limiting |
| **Infrastructure as Code** | Terraform | Declarative cloud provisioning |

---

## 6️⃣ Project Plan & Timeline

| Phase | Activities | Duration | Deadline |
|--------|-------------|-----------|-----------|
| **1. Research & Planning** | Stakeholder interviews, requirements, risk analysis | 1 Week | Oct 26, 2025 |
| **2. Design & Architecture** | C4 models, API specs, CI/CD design | 5 Days | Oct 31, 2025 |
| **3. Infrastructure Setup** | Terraform provisioning, CI/CD, monitoring setup | 1 Week | Nov 7, 2025 |
| **4. Microservice Dev** | Build core services in 8 sprints | 8 Weeks | Jan 2, 2026 |
| **5. Integration & Testing** | E2E, performance, chaos testing | 2 Weeks | Jan 16, 2026 |
| **6. UAT & Deployment** | UAT, Blue-Green deployment | 1 Week | Jan 23, 2026 |
| **7. Post-Launch Support** | Monitoring, staff training | Ongoing | — |

---

## 7️⃣ Implementation Strategy

### Agile (Scrum)
- Two-week sprints with planning, reviews, and retrospectives.
- **GitFlow branching model** for version control.
- **Code Reviews** required before merging.

### CI/CD Pipeline
- Linting → Testing → Docker Build → Deploy (Staging/Prod)
- **Blue-Green deployments** for zero-downtime releases.

### Observability
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)  
- **Metrics:** Prometheus + Grafana dashboards  
- **Tracing:** OpenTelemetry + Jaeger  

---

## 8️⃣ Evaluation & Success Metrics

### Technical KPIs
| Metric | Target | Measurement |
|---------|---------|-------------|
| System Uptime | 99.95% | Prometheus probes |
| API Latency | <200ms | API Gateway metrics |
| Error Rate | <0.1% | Service logs |
| Deployment Frequency | Daily | CI/CD logs |
| Lead Time | <1 hour | Commit → Deploy |

### Business KPIs
| Metric | Target | Measurement |
|---------|---------|-------------|
| Manual Data Entry | -80% | Staff workload reports |
| Support Tickets | -50% | Helpdesk analytics |
| Report Generation | From days → seconds | Real-time data tests |

---

## ✅ Testing Strategy

- **Unit Tests:** pytest  
- **Integration Tests:** Service-to-DB verification  
- **Contract Tests:** Pact for API compatibility  
- **E2E Tests:** Cypress simulations  
- **Performance Tests:** Locust for load testing  
- **UAT:** Staff testing in staging environment  

---

##  Conclusion

The proposed **Unified Cloud-Based Distributed System** eliminates Moodle data silos and manual data handling inefficiencies.  
By leveraging **microservices**, **event-driven communication**, and **cloud-native deployment**, this project transforms university operations — increasing agility, efficiency, and decision-making capability.

> _“This is not just a technical project; it’s a step toward a smarter, data-driven university.”_

---

### 👩🏽‍💻 Contact
**Author:** NZEKUI NZOUDJIO ALICE CRESSENCE  
📧 [nzekuinzoudjio.alice@ictu.edu.cm](mailto:nzekuinzoudjio.alice@ictu.edu.cm)  
🔗 [GitHub Repository](https://github.com/AliceCressence/Cloud-based-distributed-system)
