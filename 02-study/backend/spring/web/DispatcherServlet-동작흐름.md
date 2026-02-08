---
tags:
  - study
  - spring
  - web
  - mvc
  - dispatcher-servlet
created: 2025-02-08
---

# DispatcherServlet 동작흐름

## 한 줄 요약
> DispatcherServlet은 Spring MVC의 중앙 제어자(Front Controller)로, 모든 HTTP 요청을 받아 적절한 컨트롤러로 라우팅하고 응답을 처리하는 핵심 서블릿이다.

## 상세 설명

### DispatcherServlet이란?
- **Front Controller 패턴** 구현
- 모든 HTTP 요청의 진입점
- 요청을 적절한 핸들러(컨트롤러)에게 위임
- Spring MVC의 핵심 컴포넌트

### 왜 DispatcherServlet을 사용하는가?
```java
// DispatcherServlet 이전: 각 URL마다 서블릿 매핑
// web.xml
<servlet-mapping>
    <servlet-name>LoginServlet</servlet-name>
    <url-pattern>/login</url-pattern>
</servlet-mapping>
<servlet-mapping>
    <servlet-name>LogoutServlet</servlet-name>
    <url-pattern>/logout</url-pattern>
</servlet-mapping>
// ... 수십 개의 서블릿 매핑
```
→ 공통 기능(인코딩, 인증 등)을 각 서블릿에서 중복 처리!

### DispatcherServlet 동작 흐름

```
1. HTTP 요청
   ↓
2. DispatcherServlet (Front Controller)
   ↓
3. HandlerMapping (어떤 컨트롤러?)
   ↓
4. HandlerAdapter (컨트롤러 실행)
   ↓
5. Controller (비즈니스 로직)
   ↓
6. ModelAndView 반환
   ↓
7. ViewResolver (어떤 View?)
   ↓
8. View 렌더링
   ↓
9. HTTP 응답
```

### 주요 컴포넌트

#### 1. HandlerMapping
- **역할**: URL과 컨트롤러 메서드를 매핑
- **종류**:
  - RequestMappingHandlerMapping: @RequestMapping 처리 (기본)
  - BeanNameUrlHandlerMapping: 빈 이름으로 매핑

#### 2. HandlerAdapter
- **역할**: 다양한 타입의 컨트롤러를 실행할 수 있는 어댑터
- **종류**:
  - RequestMappingHandlerAdapter: @RequestMapping 메서드 실행
  - HttpRequestHandlerAdapter: HttpRequestHandler 처리
  - SimpleControllerHandlerAdapter: Controller 인터페이스 처리

#### 3. ViewResolver
- **역할**: 논리적 뷰 이름을 실제 뷰 객체로 변환
- **종류**:
  - InternalResourceViewResolver: JSP (기본)
  - ThymeleafViewResolver: Thymeleaf
  - JsonView: JSON 응답

#### 4. HandlerExceptionResolver
- **역할**: 컨트롤러에서 발생한 예외 처리
- @ExceptionHandler, @ControllerAdvice와 연동

### DispatcherServlet 상세 처리 과정

```
1. DispatcherServlet.doService()
   - HTTP 요청 속성 설정
   
2. DispatcherServlet.doDispatch()
   - 실제 요청 처리 로직
   
3. getHandler()
   - HandlerMapping을 순회하며 핸들러 검색
   - HandlerExecutionChain 반환 (핸들러 + 인터셉터)
   
4. getHandlerAdapter()
   - 핸들러를 실행할 수 있는 어댑터 검색
   
5. 인터셉터 preHandle() 실행
   - 컨트롤러 실행 전 전처리
   
6. HandlerAdapter.handle()
   - 실제 컨트롤러 메서드 실행
   - @RequestMapping 메서드 호출
   
7. 인터셉터 postHandle() 실행
   - 컨트롤러 실행 후, 뷰 렌더링 전
   
8. processDispatchResult()
   - ViewResolver로 View 객체 획득
   - View.render() 호출
   
9. 인터셉터 afterCompletion() 실행
   - 뷰 렌더링 후 후처리
   
10. HTTP 응답 전송
```

## 코드 예시

```java
// 1. Spring Boot에서 DispatcherServlet 자동 설정
// application.yml
spring:
  mvc:
    servlet:
      path: /  # DispatcherServlet의 URL 패턴

// 2. DispatcherServlet 커스터마이징
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Bean
    public DispatcherServlet dispatcherServlet() {
        DispatcherServlet dispatcherServlet = new DispatcherServlet();
        dispatcherServlet.setThrowExceptionIfNoHandlerFound(true);
        return dispatcherServlet;
    }
}

// 3. HandlerMapping 동작 확인
@RestController
public class TestController {
    
    @GetMapping("/test")
    public String test(HttpServletRequest request) {
        // 현재 핸들러 정보 확인
        HandlerExecutionChain chain = 
            (HandlerExecutionChain) request.getAttribute(
                HandlerMapping.BEST_MATCHING_HANDLER_ATTRIBUTE);
        return "Handler: " + chain.getHandler();
    }
}

// 4. 직접 DispatcherServlet 등록 (Spring Boot 아닐 때)
public class WebAppInitializer 
        implements WebApplicationInitializer {
    
    @Override
    public void onStartup(ServletContext servletContext) {
        // Spring 설정
        AnnotationConfigWebApplicationContext context = 
            new AnnotationConfigWebApplicationContext();
        context.register(AppConfig.class);
        
        // DispatcherServlet 등록
        DispatcherServlet servlet = new DispatcherServlet(context);
        ServletRegistration.Dynamic registration = 
            servletContext.addServlet("app", servlet);
        registration.setLoadOnStartup(1);
        registration.addMapping("/");
    }
}

// 5. HandlerInterceptor와 함께 동작
@Component
public class LoggingInterceptor implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, 
                            Object handler) {
        System.out.println("Controller 실행 전");
        return true;  // false 반환 시 컨트롤러 실행 중단
    }
    
    @Override
    public void postHandle(HttpServletRequest request, 
                          HttpServletResponse response, 
                          Object handler, 
                          ModelAndView modelAndView) {
        System.out.println("Controller 실행 후, View 렌더링 전");
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, 
                               HttpServletResponse response, 
                               Object handler, 
                               Exception ex) {
        System.out.println("View 렌더링 완료 후");
    }
}

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    
    @Autowired
    private LoggingInterceptor loggingInterceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loggingInterceptor)
                .addPathPatterns("/**")
                .excludePathPatterns("/css/**", "/js/**");
    }
}

// 6. ViewResolver 설정
@Configuration
public class ViewConfig {
    
    @Bean
    public ViewResolver viewResolver() {
        InternalResourceViewResolver resolver = 
            new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        return resolver;
    }
}

// 7. HandlerExceptionResolver 동작
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public String handleException(Exception e, Model model) {
        model.addAttribute("error", e.getMessage());
        return "error";  // ViewResolver가 처리
    }
}

// 8. @RestController vs @Controller
@RestController  // @ResponseBody가 자동 적용
public class ApiController {
    
    @GetMapping("/api/users")
    public List<User> getUsers() {
        // ViewResolver 대신 HttpMessageConverter 사용
        return userService.findAll();
    }
}

@Controller  // View 이름 반환
public class WebController {
    
    @GetMapping("/users")
    public String getUsers(Model model) {
        model.addAttribute("users", userService.findAll());
        return "users";  // ViewResolver가 처리 → users.jsp
    }
}

// 9. DispatcherServlet 초기화 과정 이해
public class MyDispatcherServlet extends DispatcherServlet {
    
    @Override
    protected void initStrategies(ApplicationContext context) {
        // 각 전략(Strategy) 컴포넌트 초기화
        initMultipartResolver(context);      // 파일 업로드
        initLocaleResolver(context);         // 국제화
        initThemeResolver(context);          // 테마
        initHandlerMappings(context);        // 핸들러 매핑
        initHandlerAdapters(context);        // 핸들러 어댑터
        initHandlerExceptionResolvers(context);  // 예외 처리
        initRequestToViewNameTranslator(context); // 뷰 이름 변환
        initViewResolvers(context);          // 뷰 리졸버
        initFlashMapManager(context);        // FlashMap 관리
    }
}
```

## 주의사항 / 함정

### 1. DispatcherServlet이 처리하지 못하는 경로
```java
// ❌ 정적 리소스까지 DispatcherServlet이 처리하려고 시도
spring:
  mvc:
    servlet:
      path: /

// ✅ 정적 리소스 처리 설정
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/static/");
    }
}
```

### 2. 인터셉터 vs 필터 실행 순서
```
Filter (doFilter)
  ↓
DispatcherServlet
  ↓
Interceptor (preHandle)
  ↓
Controller
  ↓
Interceptor (postHandle)
  ↓
View Rendering
  ↓
Interceptor (afterCompletion)
  ↓
Filter (doFilter 종료)
```

### 3. Handler를 찾지 못할 때
```java
// ❌ 기본 동작: 404 에러 페이지만 반환
spring.mvc.throw-exception-if-no-handler-found=false

// ✅ NoHandlerFoundException 발생시켜 @ControllerAdvice에서 처리
spring.mvc.throw-exception-if-no-handler-found=true
spring.web.resources.add-mappings=false
```

### 4. @ResponseBody의 동작 방식
```java
@Controller
public class MyController {
    
    @GetMapping("/data")
    @ResponseBody  // ViewResolver 대신 HttpMessageConverter 사용
    public User getUser() {
        return new User();  // JSON으로 변환되어 응답
    }
}

// @RestController = @Controller + @ResponseBody
@RestController
public class MyRestController {
    
    @GetMapping("/data")
    public User getUser() {  // 모든 메서드에 @ResponseBody 자동 적용
        return new User();
    }
}
```

### 5. DispatcherServlet의 부모-자식 컨텍스트
```java
// ❌ Service 빈을 DispatcherServlet 컨텍스트에서만 등록
@Configuration
@ComponentScan("com.example")  // Service까지 스캔
public class WebConfig { }

// ✅ 계층 분리
// Root WebApplicationContext: Service, Repository
@Configuration
@ComponentScan(basePackages = "com.example", 
               excludeFilters = @Filter(Controller.class))
public class RootConfig { }

// DispatcherServlet WebApplicationContext: Controller
@Configuration
@ComponentScan(basePackages = "com.example.web")
public class WebConfig { }
```

### 6. 여러 DispatcherServlet 등록
```java
@Bean
public ServletRegistrationBean<DispatcherServlet> apiServlet() {
    DispatcherServlet servlet = new DispatcherServlet();
    servlet.setApplicationContext(apiContext());
    return new ServletRegistrationBean<>(servlet, "/api/*");
}

@Bean
public ServletRegistrationBean<DispatcherServlet> webServlet() {
    DispatcherServlet servlet = new DispatcherServlet();
    servlet.setApplicationContext(webContext());
    return new ServletRegistrationBean<>(servlet, "/*");
}
```

## 관련 개념
- [[필터와-인터셉터]]
- [[예외처리-전략]]
- [[검증과-데이터바인딩]]

## 면접 질문

1. **DispatcherServlet의 역할은 무엇인가요?**
   - Spring MVC의 Front Controller로, 모든 HTTP 요청을 받아 적절한 컨트롤러로 라우팅
   - HandlerMapping, HandlerAdapter, ViewResolver 등을 조율

2. **DispatcherServlet의 동작 흐름을 설명하세요.**
   - 요청 → HandlerMapping(어떤 컨트롤러?) → HandlerAdapter(컨트롤러 실행) → Controller(비즈니스 로직) → ViewResolver(어떤 View?) → View 렌더링 → 응답

3. **HandlerMapping과 HandlerAdapter의 역할 차이는?**
   - HandlerMapping: URL과 컨트롤러 메서드를 매핑 (어떤 핸들러?)
   - HandlerAdapter: 다양한 타입의 컨트롤러를 실행할 수 있는 어댑터 (어떻게 실행?)

4. **@Controller와 @RestController의 차이는?**
   - @Controller: ViewResolver를 통해 View 반환
   - @RestController: HttpMessageConverter를 통해 데이터를 직접 HTTP 응답 본문에 작성

5. **DispatcherServlet과 Filter의 실행 순서는?**
   - Filter → DispatcherServlet → Interceptor → Controller → Interceptor → View

6. **DispatcherServlet이 핸들러를 찾지 못하면?**
   - 기본: 404 에러 페이지 반환
   - throw-exception-if-no-handler-found=true 설정 시: NoHandlerFoundException 발생

7. **ViewResolver가 하는 일은?**
   - 컨트롤러가 반환한 논리적 뷰 이름을 실제 View 객체로 변환
   - 예: "users" → "/WEB-INF/views/users.jsp"

## 참고 자료
- 김영한의 스프링 MVC 1편 - 백엔드 웹 개발 핵심 기술
- Spring Framework Reference - Web MVC
- https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-servlet.html
