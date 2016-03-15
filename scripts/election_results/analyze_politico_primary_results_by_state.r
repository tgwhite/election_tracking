
library(plyr)
library(dplyr)
library(reshape2)
library(ggplot2)
library(stringr)
library(data.table)
library(maps)
library(extrafont)

options(stringsAsFactors = F)

# county level geography
county_geo = map_data('county')

# read in primary election results by county and clean up variables for analysis
setwd("~/tgwhite_github/election_tracking/data/presidential_primary_election_results")
all_primary_results_by_county = fread('all_primary_results_by_county.csv')

all_primary_results_by_county_upd <- 
  all_primary_results_by_county %>%
  mutate(
    popular_vote = str_replace_all(popular_vote, pattern = ",", replacement = "") %>% as.numeric(), 
    percentage = str_replace_all(percentage, pattern = "%", replacement = "") %>% as.numeric(),
    county_clean = str_replace_all(county, pattern = 'County', replacement = '') %>% str_trim() %>% tolower(),
    state_clean = str_replace_all(state, pattern = '-', replacement = " ") %>% tolower()
  )

# get geographic data by county

hillary_bernie_results = filter(all_primary_results_by_county_upd, str_detect(candidate %>% tolower(), 'sanders|clinton')) %>%
  mutate(
    cand_clean = ifelse(str_detect(tolower(candidate), 'sanders'), 'sanders', 'clinton')
  )

# push wide and do some cleaning
dem_primary_results_wide <- dcast(hillary_bernie_results, state_clean + county_clean ~ cand_clean, value.var = 'percentage')

dem_primary_results_wide_upd <- 
  dem_primary_results_wide %>%
  mutate(
    clinton_cut = cut(clinton, breaks = seq(0, 100, by = 10), include.lowest = T)
  ) %>%
  right_join(county_geo, by = c('state_clean' = 'region', 'county_clean' = 'subregion'))


# plot clinton vs sanders
dem_primary_results_plot <- ggplot(dem_primary_results_wide_upd, aes(long, lat, group = group, fill = clinton )) +
  geom_polygon() +
  geom_path(colour = 'white') +
  theme(
    text = element_text(family = 'Garamond', face = 'bold'),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    plot.title = element_text(size = 14)
  ) +
  labs(
    y = '\n\n', x = '\n\nTaylor G. White\nSource: AP via Politico\n',  
    title = '\n2016 Democratic Primary Results by County\n3/15/16\n'
  ) +
  scale_fill_gradient2(name = 'Clinton Vote Share (%)', low = 'forestgreen', high = 'steelblue', mid = 'white', midpoint = 50)

ggsave('clinton_vs_sanders_by_county.png', plot = dem_primary_results_plot, height = 10, width = 12, units = 'in', dpi = 400)
