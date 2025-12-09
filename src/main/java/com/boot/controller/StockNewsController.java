package com.boot.controller;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.boot.dto.StockNews;
import com.boot.service.StockNewsService;

import lombok.RequiredArgsConstructor;

@CrossOrigin(origins = "http://localhost:5173")
@RestController
@RequiredArgsConstructor
@RequestMapping("/news")
public class StockNewsController {

    private final StockNewsService stockNewsService;

    /** 🔵 기존 기본 뉴스 리스트 */
    @GetMapping
    public Page<StockNews> getNews(
            @RequestParam(value = "category", required = false) String category,
            @RequestParam(value = "page", defaultValue = "0") int page,
            @RequestParam(value = "size", defaultValue = "10") int size,
            @RequestParam(value = "sort", defaultValue = "date") String sort
    ) {
        return stockNewsService.search(null, category, page, size, sort);
    }

    /** 🔵 TF-IDF 검색 API → Python 검색 서버 호출 */
    @GetMapping("/search")
    public Object searchNews(@RequestParam("q") String keyword) {

        try {
        	String pyUrl = "http://localhost:9901/news/search?q=" 
        	        + URLEncoder.encode(keyword, StandardCharsets.UTF_8);

            RestTemplate rest = new RestTemplate();
            Object result = rest.getForObject(pyUrl, Object.class);

            System.out.println("🔥 TF-IDF 검색 결과 수: " + ((List<?>) result).size());
            return result;

        } catch (Exception e) {
            e.printStackTrace();
            return List.of(); // 오류 시 빈 리스트 반환
        }
    }
}
