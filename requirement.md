# SCD Work Trial Requirements

## Project Overview
**Objective**: Build an abstraction for SCD (Slowly Changing Dimensions) implementation to simplify database queries
**Duration**: 2-4 hours
**Domain**: Database Abstraction & ORM Development
**Primary Focus**: Golang implementation with cross-language considerations

## Background & Context

### What is SCD (Slowly Changing Dimensions)?
- Read comprehensive guide: [Slowly Changing Dimensions](https://www.thoughtspot.com/data-trends/data-modeling/slowly-changing-dimensions-in-data-warehouse)
- SCD tracks historical changes to data over time
- Uses versioning to maintain data history

### Current SCD Implementation Structure
- **Unique Key**: (id, version) pair
- **Primary Key**: uid column
- **Versioning**: New version created when data changes
- **Latest Version**: Current active version for queries

### Example SCD Table Structure

**Jobs Table:**
```
| id                      | version | uid                           | status   | rate | title            | companyId           | contractorId        |
|------------------------|---------|-------------------------------|----------|------|------------------|--------------------|--------------------|
| job_ckbk6oo4hn7pacdgcz9f| 1       | job_uid_tm15dj18wal295r3xiea  | extended | 20.0 | Software Engineer| comp_cab5i8o0rvh5ar| cont_e0nhseq682vkoc|
| job_ckbk6oo4hn7pacdgcz9f| 2       | job_uid_ae51ppj9jpt56he2ua3   | active   | 20.0 | Software Engineer| comp_cab5i8o0rvh5ar| cont_e0nhseq682vkoc|
| job_ckbk6oo4hn7pacdgcz9f| 3       | job_uid_ywij5sh1tvfp5nkq7azav | active   | 15.5 | Software Engineer| comp_cab5i8o0rvh5ar| cont_e0nhseq682vkoc|
```

**Timelogs Table:**
```
| id                    | version | uid                          | duration | timeStart      | timeEnd        | type     | jobUid                       |
|----------------------|---------|------------------------------|----------|----------------|----------------|----------|------------------------------|
| tl_AAABk__7Gd2t3TqM  | 1       | tl_uid_AAABk__7Gd3uvJs1nkk5 | 1497212  | 1735164463798  | 1735165961010  | captured | job_uid_ywij5sh1tvfp5nkq7azav|
| tl_AAABk__7Gd2t3TqM  | 2       | tl_uid_AAABk__7GgmK5l5VWLv3 | 82304    | 1735164463798  | 1735165961010  | adjusted | job_uid_ywij5sh1tvfp5nkq7azav|
```

**PaymentLineItems Table:**
```
| id                   | version | uid                          | jobUid                       | timelogUid                   | amount | status   |
|---------------------|---------|------------------------------|------------------------------|------------------------------|--------|----------|
| li_AAABk__7JGVd0tli | 1       | li_uid_AAABk__7JGX02JOi4Ya  | job_uid_ywij5sh1tvfp5nkq7azav| tl_uid_AAABk__7GgmK5l5VWLv3 | 35     | not-paid |
| li_AAABk__7JGVd0tli | 2       | li_uid_AAABlB5Yf5MbU3tZyhCJ | job_uid_ywij5sh1tvfp5nkq7azav| tl_uid_AAABk__7GgmK5l5VWLv3 | 35     | paid     |
```

## Problem Statement

### Current Challenges
1. **Unoptimized Queries**: Complex SCD logic leads to inefficient database queries
2. **Code Repetition**: SCD handling logic duplicated across codebase
3. **Developer Complexity**: Teams must manually handle SCD versioning logic
4. **Performance Issues**: Millions of PaymentLineItems records require optimized SCD handling

### Common Query Patterns Requiring SCD Abstraction
1. Get all active Jobs for a company (latest version filtering)
2. Get all active Jobs for a contractor (latest version filtering)
3. Get all PaymentLineItems for a contractor in a time period (latest versions only)
4. Get all Timelogs for a contractor in a time period (latest versions only)

## Technical Requirements

### 1. Technology Stack
- **Primary Language**: Golang
- **ORM**: GORM ([Documentation](https://gorm.io/index.html))
- **Secondary Context**: Django ORM ([Documentation](https://docs.djangoproject.com/en/5.1/topics/db/queries/))
- **Database**: SQL-based (PostgreSQL/MySQL implied)

### 2. Development Environment
- [ ] Golang development environment
- [ ] GORM library access
- [ ] Understanding of SCD concepts
- [ ] Database query optimization knowledge

## Task Breakdown

### Phase 1: Analysis & Understanding (20-30 minutes)
- [ ] Study SCD table structures and relationships
- [ ] Analyze current query patterns and pain points
- [ ] Understand GORM capabilities and limitations
- [ ] Review example tables and data relationships

### Phase 2: Design SCD Abstraction (30-45 minutes)
- [ ] Design abstraction interface for SCD operations
- [ ] Plan query optimization strategies
- [ ] Design version handling mechanisms
- [ ] Consider foreign key relationships (uid-based)

### Phase 3: Golang Implementation (60-90 minutes)
- [ ] Implement SCD abstraction layer using GORM
- [ ] Create helper functions for latest version queries
- [ ] Implement efficient filtering mechanisms
- [ ] Handle SCD update operations (versioning)

### Phase 4: Query Examples & Testing (20-30 minutes)
- [ ] Demonstrate abstraction with example queries
- [ ] Show before/after code comparison
- [ ] Validate query efficiency
- [ ] Test edge cases and error handling

### Phase 5: Cross-Language Strategy (15-20 minutes - Stretch Goal)
- [ ] Design language-agnostic abstraction approach
- [ ] Propose centralized SCD handling strategy
- [ ] Consider database-level vs application-level solutions

## Specific Deliverables

### 1. Core SCD Abstraction (Golang/GORM)
**Required Features**:
- [ ] **Latest Version Query Helper**: Abstract latest version filtering
- [ ] **SCD Create/Update Operations**: Handle versioning automatically
- [ ] **Efficient Filtering**: Optimize queries for large datasets
- [ ] **Foreign Key Handling**: Support uid-based relationships

### 2. Query Examples
**Demonstrate abstraction with these queries**:
- [ ] Get all active Jobs for a company
- [ ] Get all active Jobs for a contractor  
- [ ] Get PaymentLineItems for contractor in time period
- [ ] Get Timelogs for contractor in time period

### 3. Performance Considerations
- [ ] Query optimization for millions of records
- [ ] Efficient indexing strategy recommendations
- [ ] Batch operation support

### 4. Cross-Language Strategy (Stretch)
- [ ] Design centralized abstraction approach
- [ ] Language-agnostic interface definition
- [ ] Implementation strategy for Django integration

## AI Agent Implementation Guide

### Pre-Implementation Checklist
1. **SCD Concept Validation**:
   ```go
   // Understand SCD structure
   type SCDModel struct {
       ID      string `gorm:"index:idx_id_version,unique"`
       Version int    `gorm:"index:idx_id_version,unique"`
       UID     string `gorm:"primarykey"`
       // ... other fields
   }
   ```

2. **GORM Familiarity**:
   - Query building patterns
   - Subquery support
   - Performance optimization techniques
   - Custom scope definitions

### Implementation Strategy
1. **Create SCD Interface**:
   ```go
   type SCDRepository interface {
       FindLatest(conditions interface{}) ([]interface{}, error)
       CreateVersion(model interface{}) error
       UpdateWithVersion(id string, updates interface{}) error
   }
   ```

2. **Query Optimization Patterns**:
   - Use window functions for latest version queries
   - Implement efficient subqueries
   - Consider database-specific optimizations

3. **Example Implementation Structure**:
   ```go
   // Before abstraction
   db.Table("jobs").
       Select("jobs.*").
       Joins("JOIN (SELECT id, MAX(version) as max_version FROM jobs GROUP BY id) latest ON jobs.id = latest.id AND jobs.version = latest.max_version").
       Where("status = ?", "active").
       Find(&jobs)

   // After abstraction
   scdRepo.FindLatestWhere("jobs", "status = ?", "active").Find(&jobs)
   ```

### Testing Strategy
- [ ] **Unit Tests**: Test abstraction functions
- [ ] **Performance Tests**: Validate query efficiency
- [ ] **Integration Tests**: Test with real SCD data
- [ ] **Edge Case Tests**: Handle version conflicts, concurrent updates

## Evaluation Criteria

### Technical Implementation (50%)
- Correct understanding of SCD concepts
- Efficient GORM implementation
- Query optimization techniques
- Code organization and reusability

### Problem-Solving Approach (30%)
- Identification of core abstraction needs
- Creative solutions for performance challenges
- Handling of edge cases and error scenarios

### Code Quality (20%)
- Clean, readable Golang code
- Proper GORM usage patterns
- Documentation and examples
- Interface design quality

## Success Metrics
- [ ] **Functional**: Abstraction handles all required query patterns
- [ ] **Performance**: Optimized queries for large datasets
- [ ] **Usability**: Simple interface for developers
- [ ] **Extensible**: Easy to add new SCD operations
- [ ] **Cross-Language**: Viable strategy for Django integration

## Common Pitfalls to Avoid
- [ ] **Over-Engineering**: Keep abstraction simple and focused
- [ ] **Performance Neglect**: Optimize for millions of records
- [ ] **Version Conflicts**: Handle concurrent version creation
- [ ] **Foreign Key Issues**: Properly handle uid-based relationships
- [ ] **Query Complexity**: Avoid N+1 query problems

## Example Code Structure Expected
```go
// SCD abstraction interface
type SCDManager interface {
    GetLatestRecords(tableName string, conditions map[string]interface{}) error
    CreateNewVersion(model SCDModel) error
    UpdateRecord(id string, updates map[string]interface{}) error
}

// Usage examples
jobManager := NewSCDManager[Job](db)
activeJobs := jobManager.FindLatestWhere("status = ?", "active")

lineItemManager := NewSCDManager[PaymentLineItem](db)
contractorItems := lineItemManager.FindLatestWhere("contractor_id = ? AND created_at BETWEEN ? AND ?", contractorID, startDate, endDate)
```

## Stretch Goal: Cross-Language Centralization
**Possible Approaches**:
1. **Database Views/Functions**: Create database-level SCD views
2. **GraphQL Layer**: Centralized API with SCD handling
3. **Microservice**: Dedicated SCD service for all applications
4. **Code Generation**: Generate SCD code for multiple languages

## Additional Resources
- [GORM Advanced Queries](https://gorm.io/docs/advanced_query.html)
- [Database Indexing Strategies](https://use-the-index-luke.com/)
- [SCD Implementation Patterns](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/slowly-changing-dimension/)

## Submission Requirements
1. **Complete Golang Implementation**: Working SCD abstraction with GORM
2. **Query Examples**: Demonstrate all 4 required query patterns
3. **Performance Analysis**: Explain optimization strategies
4. **Cross-Language Strategy**: High-level approach for centralization
5. **Documentation**: Clear usage examples and API documentation

## FAQ Support
- **AI Tools Usage**: Encouraged for syntax, documentation, and examples
- **Focus**: Understand and explain all generated code
- **Time Management**: Prioritize core Golang implementation over stretch goals

---

**Note**: This work trial tests your ability to design database abstractions, optimize queries, and create developer-friendly interfaces. Focus on practical solutions that solve real performance and maintainability challenges.
