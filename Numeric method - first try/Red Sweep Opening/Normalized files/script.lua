-- Lua script for Fityk.
 prev_y = nil
 for n = 0, F:get_dataset_count()-1 do
    local path = F:get_info("filename", n)
    local filename = string.match(path, "[^/\\]+$") or ""
    local y1 = F:calculate_expr("F[0].center", n)
    local y2 = F:calculate_expr("F[0].height", n)
    local y3 = F:calculate_expr("F[0].hwhm", n)
    local y4 = F:calculate_expr("F[1].a", n)  
    s = string.format("%02d\t%.4f\t%.4f\t%.4f\t%.4f", n, n*0.5, y1, y2, y3, y4)
    print(s)
end
