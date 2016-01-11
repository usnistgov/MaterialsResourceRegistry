<?xml version="1.0" encoding="UTF-8"?>
<!--
################################################################################
#
# File Name: xml2html.xsl
# Purpose: 	Renders an XML document in HTML  
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################ 
 -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="1.0">
	<xsl:output method="html" indent="yes" encoding="UTF-8" />
	<xsl:preserve-space elements="*" />
	<xsl:template match="/">	 	
		<ul class="tree">
		<xsl:apply-templates />
		</ul>
	</xsl:template>
	<xsl:template match="*">
		<li>
		<div class="element-wrapper">
			<!-- no left indent for root element -->
			<xsl:if test="not(ancestor::*)">
				<xsl:attribute name="style">left:0</xsl:attribute>
			</xsl:if>			
			<xsl:choose>
				<xsl:when test="*">
					<span class="collapse" style="cursor:pointer;" onclick="showhide(event);"></span>
					<span class="category">						
						<xsl:value-of select="name(.)" />
					</span>
				</xsl:when>					
				<xsl:otherwise>
					<span class="element">
						<xsl:value-of select="name(.)" />
					</span>
				</xsl:otherwise>
			</xsl:choose>
			<!-- attributes -->
			<xsl:for-each select="@*">
				<span class="type">
				<xsl:value-of select="name(.)" />:<xsl:value-of select="."/>
				</span>
			</xsl:for-each>
			<xsl:choose>
				<xsl:when test="not(*)">
					<xsl:text> : </xsl:text>
					<xsl:apply-templates />
				</xsl:when>
				<xsl:otherwise>
					<ul>
						<xsl:apply-templates />
					</ul>
				</xsl:otherwise>				
			</xsl:choose>
		</div>
		</li>
	</xsl:template>
	<xsl:template match="text()">
		<xsl:variable name="class">
			<xsl:choose>
				<xsl:when test="parent::*[@xml:space='preserve']">
					<xsl:value-of select="'text preserve'" />
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="'text'" />
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<span class="{$class}">
			<xsl:value-of select="." />
		</span>
	</xsl:template>
</xsl:stylesheet>